from __future__ import annotations

import base64
import hashlib
import hmac
import json
import sys
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from merge_authorization import (
    MergeAuthorizationError,
    ReplayStore,
    build_authorization_request,
    build_public_check_output,
    canonical_digest,
    sign_attestation,
    validate_webhook_signature,
    verify_attestation,
)

KEY_B64 = base64.b64encode(bytes(range(32))).decode("ascii")
HEAD_SHA = "a" * 40
BASE_SHA = "b" * 40
TARGET_SHA = BASE_SHA
NONCE = "e" * 64
POLICY = {
    "gate_policy": {"G3_DESIGN": {"roles": ["architect"], "min_approvals": 1}},
    "trusted_identity": {"providers": ["company-oidc"], "require_commit_sha": True},
}


def approval_record() -> dict:
    return {
        "approval_id": "APR-G3-ID-V1-" + "A" * 64,
        "change_id": "CHG-2026-003",
        "gate": "G3_DESIGN",
        "decision": "approved",
        "actor_id": "ghoidc-v1:" + "1" * 64,
        "actor_role": "architect",
        "decided_at": "2026-07-17T00:00:00Z",
        "evidence_ids": ["EVD-G3-DESIGN-REVIEW"],
        "identity_provider": "company-oidc",
        "identity_claim": "sandbox-reduced-claim",
        "commit_sha": TARGET_SHA,
    }


def approval_bytes() -> bytes:
    return json.dumps(approval_record(), sort_keys=True, separators=(",", ":")).encode("utf-8")


def approval_file(content: bytes | None = None) -> dict:
    raw = approval_bytes() if content is None else content
    return {
        "path": "changes/CHG-2026-003-private-gate-role-injection/approvals/APR-G3-ID-V1-" + "A" * 64 + ".json",
        "status": "added",
        "size": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "is_symlink": False,
        "is_submodule": False,
    }


def build_request(**overrides) -> dict:
    raw = approval_bytes()
    values = {
        "repository_id": "123",
        "pull_request": 7,
        "head_sha": HEAD_SHA,
        "base_sha": BASE_SHA,
        "base_ref": "main",
        "files": [approval_file(raw)],
        "approval_content": raw,
        "policy": POLICY,
        "known_evidence_ids": {"EVD-G3-DESIGN-REVIEW"},
        "nonce": NONCE,
        "issued_at": 1_000,
        "expires_at": 1_300,
    }
    values.update(overrides)
    return build_authorization_request(**values)


class MergeAuthorizationTests(unittest.TestCase):
    def test_contract_schemas_accept_generated_documents(self):
        request = build_request()
        attestation = sign_attestation(
            request,
            decision="approved",
            review_policy_result="passed",
            control_workflow_ref="private-control/workflow@immutable-ref",
            key_b64=KEY_B64,
            issued_at=1_010,
            expires_at=1_200,
        )
        for schema_name, document in [
            ("merge-authorization-request.schema.json", request),
            ("merge-authorization-attestation.schema.json", attestation),
        ]:
            schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
            Draft202012Validator(schema).validate(document)

    def test_single_approval_diff_builds_commit_bound_request(self):
        request = build_request()
        self.assertEqual(request["classification"], "approval")
        self.assertEqual(request["head_sha"], HEAD_SHA)
        self.assertEqual(request["target_commit"], TARGET_SHA)
        self.assertEqual(request["change_id"], "CHG-2026-003")
        self.assertEqual(request["approval_sha256"], hashlib.sha256(approval_bytes()).hexdigest())
        self.assertEqual(request["policy_sha256"], canonical_digest(POLICY))
        self.assertRegex(canonical_digest(request), r"^[a-f0-9]{64}$")

    def test_non_approval_diff_is_explicit_not_applicable(self):
        request = build_request(
            files=[{
                "path": "README.md", "status": "modified", "size": 10,
                "sha256": "f" * 64, "is_symlink": False, "is_submodule": False,
            }],
            approval_content=None,
        )
        self.assertEqual(request["classification"], "not_applicable")
        self.assertIsNone(request["approval_path"])
        output = build_public_check_output(request, attestation=None)
        self.assertEqual(output["conclusion"], "success")
        self.assertEqual(output["classification"], "not_applicable")

    def test_mixed_modified_or_unsafe_approval_diff_fails_closed(self):
        raw = approval_bytes()
        cases = [
            [approval_file(raw), {"path": "README.md", "status": "modified", "size": 1, "sha256": "0" * 64, "is_symlink": False, "is_submodule": False}],
            [{**approval_file(raw), "status": "modified"}],
            [{**approval_file(raw), "is_symlink": True}],
            [{**approval_file(raw), "is_submodule": True}],
            [{**approval_file(raw), "path": "changes/CHG-2026-003-private-gate-role-injection/approvals/../escape.json"}],
        ]
        for files in cases:
            with self.subTest(files=files):
                with self.assertRaises(MergeAuthorizationError):
                    build_request(files=files)

    def test_approval_content_and_diff_metadata_must_match(self):
        raw = approval_bytes()
        with self.assertRaises(MergeAuthorizationError):
            build_request(files=[{**approval_file(raw), "sha256": "0" * 64}])
        with self.assertRaises(MergeAuthorizationError):
            build_request(files=[{**approval_file(raw), "size": len(raw) + 1}])
        duplicate = raw[:-1] + b',"change_id":"CHG-2026-999"}'
        with self.assertRaises(MergeAuthorizationError):
            build_request(files=[approval_file(duplicate)], approval_content=duplicate)

    def test_attestation_is_exact_head_expiring_and_fail_closed(self):
        request = build_request()
        attestation = sign_attestation(
            request,
            decision="approved",
            review_policy_result="passed",
            control_workflow_ref="private-control/workflow@immutable-ref",
            key_b64=KEY_B64,
            issued_at=1_010,
            expires_at=1_200,
        )
        verify_attestation(
            request, attestation, key_b64=KEY_B64,
            current_head_sha=HEAD_SHA, current_base_sha=BASE_SHA,
            current_policy=POLICY, now=1_100,
        )
        mutations = [
            {"current_head_sha": "9" * 40, "current_base_sha": BASE_SHA, "current_policy": POLICY, "now": 1_100},
            {"current_head_sha": HEAD_SHA, "current_base_sha": "8" * 40, "current_policy": POLICY, "now": 1_100},
            {"current_head_sha": HEAD_SHA, "current_base_sha": BASE_SHA, "current_policy": POLICY, "now": 1_201},
            {"current_head_sha": HEAD_SHA, "current_base_sha": BASE_SHA, "current_policy": {**POLICY, "changed": True}, "now": 1_100},
        ]
        for values in mutations:
            with self.subTest(values=values):
                with self.assertRaises(MergeAuthorizationError):
                    verify_attestation(request, attestation, key_b64=KEY_B64, **values)
        tampered = dict(attestation)
        tampered["request_digest"] = "0" * 64
        with self.assertRaises(MergeAuthorizationError):
            verify_attestation(
                request, tampered, key_b64=KEY_B64,
                current_head_sha=HEAD_SHA, current_base_sha=BASE_SHA,
                current_policy=POLICY, now=1_100,
            )

    def test_denied_or_failed_private_review_never_succeeds(self):
        request = build_request()
        for decision, review in [("denied", "failed"), ("approved", "failed")]:
            attestation = sign_attestation(
                request, decision=decision, review_policy_result=review,
                control_workflow_ref="private-control/workflow@immutable-ref",
                key_b64=KEY_B64, issued_at=1_010, expires_at=1_200,
            )
            with self.assertRaises(MergeAuthorizationError):
                verify_attestation(
                    request, attestation, key_b64=KEY_B64,
                    current_head_sha=HEAD_SHA, current_base_sha=BASE_SHA,
                    current_policy=POLICY, now=1_100,
                )

    def test_webhook_signature_uses_sha256_hmac(self):
        body = b'{"action":"synchronize"}'
        secret = b"sandbox-webhook-secret"
        signature = "sha256=" + hmac.new(secret, body, hashlib.sha256).hexdigest()
        validate_webhook_signature(body, signature, secret)
        for invalid in ["", "sha1=" + "0" * 40, "sha256=" + "0" * 64, signature.upper()]:
            with self.subTest(signature=invalid):
                with self.assertRaises(MergeAuthorizationError):
                    validate_webhook_signature(body, invalid, secret)

    def test_replay_store_is_private_atomic_and_idempotent(self):
        request_digest = canonical_digest(build_request())
        with tempfile.TemporaryDirectory() as temporary:
            store = ReplayStore(Path(temporary))
            self.assertEqual(store.claim("delivery-1", request_digest, now=1_000), "new")
            self.assertEqual(store.claim("delivery-1", request_digest, now=1_001), "duplicate")
            with self.assertRaises(MergeAuthorizationError):
                store.claim("delivery-1", "0" * 64, now=1_002)
            content = "".join(path.read_text(encoding="utf-8") for path in Path(temporary).iterdir())
            self.assertNotIn("delivery-1", content)

    def test_public_output_is_allowlisted_and_contains_no_private_identity(self):
        request = build_request()
        private_ref = "private-control/reviewer-login/team-secret@immutable-ref"
        attestation = sign_attestation(
            request, decision="approved", review_policy_result="passed",
            control_workflow_ref=private_ref, key_b64=KEY_B64,
            issued_at=1_010, expires_at=1_200,
        )
        output = build_public_check_output(
            request, attestation=attestation, key_b64=KEY_B64,
            current_head_sha=HEAD_SHA, current_base_sha=BASE_SHA,
            current_policy=POLICY, now=1_100,
        )
        self.assertEqual(output["conclusion"], "success")
        self.assertEqual(set(output), {
            "schema_version", "check_name", "conclusion", "classification",
            "repository_id", "pull_request", "head_sha", "change_id",
            "approval_sha256", "attestation_digest",
        })
        serialized = json.dumps(output, sort_keys=True)
        self.assertNotIn(private_ref, serialized)
        self.assertNotIn("reviewer-login", serialized)
        self.assertNotIn("team-secret", serialized)

    def test_unverified_attestation_cannot_produce_success_output(self):
        request = build_request()
        attestation = sign_attestation(
            request, decision="approved", review_policy_result="passed",
            control_workflow_ref="private-control/workflow@immutable-ref",
            key_b64=KEY_B64, issued_at=1_010, expires_at=1_200,
        )
        with self.assertRaises(MergeAuthorizationError):
            build_public_check_output(request, attestation=attestation)

    def test_approval_target_must_equal_fresh_base_commit(self):
        record = approval_record()
        record["commit_sha"] = "c" * 40
        raw = json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")
        with self.assertRaises(MergeAuthorizationError):
            build_request(files=[approval_file(raw)], approval_content=raw)

    def test_public_policy_is_sandbox_only_and_least_privilege(self):
        policy = json.loads(
            (ROOT / "config" / "merge-authorization-policy.json").read_text(encoding="utf-8")
        )
        self.assertEqual(policy["mode"], "sandbox-only")
        self.assertFalse(policy["production_activation"])
        self.assertTrue(policy["expected_source"].startswith("REPLACE_WITH_"))
        self.assertEqual(policy["github_app_permissions"], {
            "metadata": "read", "pull_requests": "read",
            "contents": "read", "checks": "write",
        })
        self.assertEqual(policy["ruleset"]["bypass_actors"], [])
        self.assertFalse(policy["private_environment"]["allow_admin_bypass"])


if __name__ == "__main__":
    unittest.main()
