from __future__ import annotations

import base64
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from device_flow_authorization import (
    DeviceAuthorizationError,
    FreshDeviceSessionStore,
    authorize_device_identity,
    build_device_public_check_output,
    sign_device_attestation,
    validate_poll_freshness,
    verify_device_attestation,
)
from gate_identity import actor_pseudonym
from merge_authorization import build_authorization_request, canonical_digest

KEY_B64 = base64.b64encode(bytes(range(32))).decode("ascii")
PEPPER_B64 = base64.b64encode(bytes(reversed(range(32)))).decode("ascii")
HEAD_SHA = "a" * 40
BASE_SHA = "b" * 40
SESSION_DIGEST = "1" * 64
CONTROLLER_DIGEST = "2" * 64
CONFIG_DIGEST = "3" * 64
APP_DIGEST = "4" * 64
INSTALLATION_DIGEST = "5" * 64
GATE_POLICY = {
    "gate_policy": {"G3_DESIGN": {"roles": ["architect"], "min_approvals": 1}},
    "trusted_identity": {"providers": ["company-oidc"], "require_commit_sha": True},
}


def merge_policy() -> dict:
    return json.loads(
        (ROOT / "config" / "merge-authorization-policy.json").read_text(encoding="utf-8")
    )


def approval_bytes(actor_ref: str | None = None) -> bytes:
    document = {
        "approval_id": "APR-G3-ID-V1-" + "A" * 64,
        "change_id": "CHG-2026-003",
        "gate": "G3_DESIGN",
        "decision": "approved",
        "actor_id": actor_ref or actor_pseudonym("123", "700", PEPPER_B64),
        "actor_role": "architect",
        "decided_at": "2026-07-17T00:00:00Z",
        "evidence_ids": ["EVD-G3-DESIGN-REVIEW"],
        "identity_provider": "company-oidc",
        "identity_claim": "sandbox-reduced-claim",
        "commit_sha": BASE_SHA,
    }
    return json.dumps(document, sort_keys=True, separators=(",", ":")).encode("utf-8")


def request(actor_ref: str | None = None) -> tuple[dict, str]:
    raw = approval_bytes(actor_ref)
    path = "changes/CHG-2026-003-private-gate-role-injection/approvals/APR-G3-ID-V1-" + "A" * 64 + ".json"
    item = {
        "path": path, "status": "added", "size": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "is_symlink": False, "is_submodule": False,
    }
    built = build_authorization_request(
        repository_id="123", pull_request=7, head_sha=HEAD_SHA,
        base_sha=BASE_SHA, base_ref="main", files=[item],
        approval_content=raw, policy=GATE_POLICY,
        known_evidence_ids={"EVD-G3-DESIGN-REVIEW"}, nonce="e" * 64,
        issued_at=1_000, expires_at=1_300,
    )
    return built, json.loads(raw)["actor_id"]


def private_role_map(roles: list[str] | None = None) -> str:
    return json.dumps({
        "schema_version": "1.0",
        "actors": {"800": roles or ["change_manager"]},
    }, separators=(",", ":"))


def verification_values() -> dict:
    return {
        "key_b64": KEY_B64,
        "current_head_sha": HEAD_SHA,
        "current_base_sha": BASE_SHA,
        "current_policy": GATE_POLICY,
        "current_installation_scope_digest": INSTALLATION_DIGEST,
        "controller_artifact_digest": CONTROLLER_DIGEST,
        "configuration_digest": CONFIG_DIGEST,
        "app_id_digest": APP_DIGEST,
        "now": 1_100,
    }


class DeviceFlowAuthorizationTests(unittest.TestCase):
    def _authorize(self, built: dict, actor_ref: str, **overrides) -> str:
        values = {
            "authenticated_user_id": "800",
            "pull_request_author_id": "900",
            "approval_actor_ref": actor_ref,
            "private_role_map_json": private_role_map(),
            "private_policy": merge_policy()["private_authorization"],
            "identity_pepper_b64": PEPPER_B64,
            "device_session_digest": SESSION_DIGEST,
        }
        values.update(overrides)
        return authorize_device_identity(built, **values)

    def _attestation(self, built: dict, decision_digest: str) -> dict:
        return sign_device_attestation(
            built, identity_decision_digest=decision_digest,
            device_session_digest=SESSION_DIGEST,
            controller_artifact_digest=CONTROLLER_DIGEST,
            configuration_digest=CONFIG_DIGEST, app_id_digest=APP_DIGEST,
            installation_scope_digest=INSTALLATION_DIGEST,
            key_b64=KEY_B64, issued_at=1_010, expires_at=1_200,
        )

    def test_fresh_numeric_change_manager_produces_schema_valid_v2_check(self):
        built, actor_ref = request()
        decision_digest = self._authorize(built, actor_ref)
        attestation = self._attestation(built, decision_digest)
        schema = json.loads(
            (ROOT / "schemas" / "merge-authorization-attestation-v2.schema.json")
            .read_text(encoding="utf-8")
        )
        Draft202012Validator(schema).validate(attestation)
        output = build_device_public_check_output(
            built, attestation, **verification_values()
        )
        self.assertEqual(output["conclusion"], "success")
        self.assertEqual(output["head_sha"], HEAD_SHA)
        self.assertEqual(set(output), {
            "schema_version", "check_name", "conclusion", "classification",
            "repository_id", "pull_request", "head_sha", "change_id",
            "approval_sha256", "attestation_digest",
        })

    def test_unknown_ambiguous_or_incompatible_private_role_fails_closed(self):
        built, actor_ref = request()
        cases = [
            private_role_map(["app_operator"]),
            private_role_map(["change_manager", "app_operator"]),
            json.dumps({"schema_version": "1.0", "actors": {}}, separators=(",", ":")),
            private_role_map(["unknown_role"]),
        ]
        for mapping in cases:
            with self.subTest(mapping=mapping):
                with self.assertRaises(DeviceAuthorizationError):
                    self._authorize(built, actor_ref, private_role_map_json=mapping)

    def test_pr_author_and_approval_actor_separation_is_mandatory(self):
        built, actor_ref = request()
        with self.assertRaises(DeviceAuthorizationError):
            self._authorize(built, actor_ref, pull_request_author_id="800")
        same_actor_ref = actor_pseudonym("123", "800", PEPPER_B64)
        built, _ = request(same_actor_ref)
        with self.assertRaises(DeviceAuthorizationError):
            self._authorize(built, same_actor_ref)

    def test_device_session_is_single_use_even_for_same_request(self):
        built, _ = request()
        with tempfile.TemporaryDirectory() as temporary:
            store = FreshDeviceSessionStore(Path(temporary))
            store.claim(SESSION_DIGEST, canonical_digest(built), now=1_000)
            with self.assertRaises(DeviceAuthorizationError) as context:
                store.claim(SESSION_DIGEST, canonical_digest(built), now=1_001)
            self.assertEqual(context.exception.code, "device_session_reused")

    def test_head_base_policy_installation_or_controller_change_is_stale(self):
        built, actor_ref = request()
        attestation = self._attestation(built, self._authorize(built, actor_ref))
        cases = [
            {"current_head_sha": "9" * 40},
            {"current_base_sha": "8" * 40},
            {"current_policy": {**GATE_POLICY, "changed": True}},
            {"current_installation_scope_digest": "6" * 64},
            {"controller_artifact_digest": "7" * 64},
            {"configuration_digest": "8" * 64},
            {"app_id_digest": "9" * 64},
            {"now": 1_201},
        ]
        for mutation in cases:
            values = verification_values()
            values.update(mutation)
            with self.subTest(mutation=mutation):
                with self.assertRaises(DeviceAuthorizationError):
                    verify_device_attestation(built, attestation, **values)

    def test_poll_expiry_and_nonapproval_device_authorization_fail_closed(self):
        built, actor_ref = request()
        with self.assertRaises(DeviceAuthorizationError):
            validate_poll_freshness(
                built, current_head_sha=HEAD_SHA, current_base_sha=BASE_SHA,
                current_policy=GATE_POLICY,
                current_installation_scope_digest=INSTALLATION_DIGEST,
                expected_installation_scope_digest=INSTALLATION_DIGEST,
                now=1_301,
            )
        nonapproval = build_authorization_request(
            repository_id="123", pull_request=8, head_sha=HEAD_SHA,
            base_sha=BASE_SHA, base_ref="main",
            files=[{
                "path": "README.md", "status": "modified", "size": 1,
                "sha256": "f" * 64, "is_symlink": False, "is_submodule": False,
            }], approval_content=None, policy=GATE_POLICY,
            known_evidence_ids=set(), nonce="d" * 64,
            issued_at=1_000, expires_at=1_300,
        )
        with self.assertRaises(DeviceAuthorizationError):
            self._authorize(nonapproval, actor_ref)

    def test_public_artifacts_contain_no_identity_mapping_or_device_material(self):
        built, actor_ref = request()
        mapping = private_role_map()
        decision_digest = self._authorize(
            built, actor_ref, private_role_map_json=mapping
        )
        attestation = self._attestation(built, decision_digest)
        output = build_device_public_check_output(
            built, attestation, **verification_values()
        )
        serialized = json.dumps(
            {"attestation": attestation, "output": output}, sort_keys=True
        )
        for private_value in ("800", "900", mapping, "change_manager", actor_ref):
            self.assertNotIn(private_value, serialized)
        for forbidden_key in ("device_code", "user_code", "access_token", "refresh_token"):
            self.assertNotIn(forbidden_key, serialized)

    def test_public_policy_keeps_gate_roles_separate_and_polling_bounded(self):
        policy = merge_policy()
        private = policy["private_authorization"]
        self.assertEqual(private["role_namespace"], "merge-authorization/v1")
        self.assertEqual(private["eligible_authorizer_roles"], ["change_manager"])
        self.assertFalse(private["refresh_token_storage"])
        self.assertTrue(private["fresh_device_flow_per_decision"])
        self.assertFalse(policy["private_environment"]["active"])
        polling = policy["polling"]
        self.assertLessEqual(polling["interval_seconds"], 300)
        self.assertLessEqual(polling["api_timeout_seconds"], 30)
        self.assertLessEqual(polling["max_retries"], 3)
        enterprise = json.loads(
            (ROOT / "config" / "enterprise-policy.json").read_text(encoding="utf-8")
        )
        self.assertNotIn("change_manager", enterprise["allowed_roles"])


if __name__ == "__main__":
    unittest.main()
