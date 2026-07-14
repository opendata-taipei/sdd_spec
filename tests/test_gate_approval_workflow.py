from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]
PEPPER = base64.b64encode(bytes(range(32))).decode("ascii")
WORKFLOW_REF = "opendata-taipei/sdd_spec/.github/workflows/sdd-gate-approval.yml@refs/heads/main"


def b64url(value: dict) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def response(now: int) -> str:
    claims = {
        "iss": "https://token.actions.githubusercontent.com",
        "aud": "sdd-approval",
        "repository_id": "111",
        "actor_id": "222",
        "workflow_ref": WORKFLOW_REF,
        "run_id": "333",
        "iat": now - 10,
        "nbf": now - 10,
        "exp": now + 300,
        "actor": "private-login",
        "sub": "private-subject",
        "jti": "private-jti",
    }
    token = f"{b64url({'alg': 'RS256', 'typ': 'JWT'})}.{b64url(claims)}.c2ln"
    return json.dumps({"value": token})


class GateApprovalWorkflowTests(unittest.TestCase):
    def trusted_env(self) -> dict[str, str]:
        env = os.environ.copy()
        env.update({
            "SDD_GITHUB_ROLE_MAP_JSON": json.dumps({
                "schema_version": "1.0", "actors": {"222": ["engineering_lead"]}
            }),
            "SDD_IDENTITY_PEPPER_B64": PEPPER,
            "GITHUB_REPOSITORY_ID": "111",
            "GITHUB_ACTOR_ID": "222",
            "GITHUB_WORKFLOW_REF": WORKFLOW_REF,
            "GITHUB_RUN_ID": "333",
            "GITHUB_SHA": "a" * 40,
        })
        return env

    def test_prepare_identity_emits_only_safe_outputs(self):
        with tempfile.TemporaryDirectory(prefix="sdd-identity-") as base:
            oidc = Path(base) / "oidc.json"
            output = Path(base) / "output.txt"
            oidc.write_text(response(int(time.time())), encoding="utf-8")
            result = subprocess.run([
                sys.executable, str(SOURCE / "scripts/prepare_gate_identity.py"),
                "--oidc-response", str(oidc), "--gate", "G4_READY",
                "--output", str(output),
            ], cwd=SOURCE, env=self.trusted_env(), text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(result.stdout, "")
            values = output.read_text(encoding="utf-8")
            self.assertIn("actor_id=ghoidc-v1:", values)
            self.assertIn("actor_role=engineering_lead", values)
            self.assertNotIn("private-login", values)
            self.assertNotIn("private-subject", values)
            self.assertNotIn("private-jti", values)
            self.assertNotIn('"actor_id":"222"', values)
            self.assertNotIn(PEPPER, values)
            self.assertNotIn(self.trusted_env()["SDD_GITHUB_ROLE_MAP_JSON"], values)

    def test_approval_is_atomic_safe_and_enterprise_valid(self):
        with tempfile.TemporaryDirectory(prefix="sdd-approval-") as base:
            root = Path(base) / "kit"
            shutil.copytree(SOURCE, root, ignore=shutil.ignore_patterns("__pycache__", "dist"))
            oidc = Path(base) / "oidc.json"
            output = Path(base) / "output.txt"
            oidc.write_text(response(int(time.time())), encoding="utf-8")
            env = self.trusted_env()
            prepared = subprocess.run([
                sys.executable, str(root / "scripts/prepare_gate_identity.py"),
                "--oidc-response", str(oidc), "--gate", "G4_READY", "--output", str(output),
            ], cwd=root, env=env, text=True, capture_output=True)
            self.assertEqual(prepared.returncode, 0, prepared.stdout + prepared.stderr)
            for line in output.read_text(encoding="utf-8").splitlines():
                key, value = line.split("=", 1)
                env["SDD_" + key.upper()] = value
            env.update({
                "SDD_CHANGE_INPUT": "CHG-2026-003",
                "SDD_GATE_INPUT": "G4_READY",
                "SDD_EVIDENCE_IDS_INPUT": "EVD-G4-IMPLEMENTATION-READINESS",
                "SDD_IDENTITY_PROVIDER": "github-oidc",
            })
            command = [sys.executable, str(root / "scripts/create_approval.py"), "--from-env"]
            created = subprocess.run(command, cwd=root, env=env, text=True, capture_output=True)
            self.assertEqual(created.returncode, 0, created.stdout + created.stderr)
            relative = created.stdout.strip()
            self.assertRegex(relative, r"/approvals/APR-G4-ID-V1-[A-F0-9]{64}\.json$")
            target = root / relative
            self.assertTrue(target.is_file())
            self.assertNotIn(":", target.name)
            original = target.read_bytes()
            duplicate = subprocess.run(command, cwd=root, env=env, text=True, capture_output=True)
            self.assertNotEqual(duplicate.returncode, 0)
            self.assertEqual(target.read_bytes(), original)
            self.assertFalse(list(target.parent.glob("*.tmp")))
            validated = subprocess.run(
                [sys.executable, str(root / "scripts/validate_enterprise.py")],
                cwd=root, text=True, capture_output=True,
            )
            self.assertEqual(validated.returncode, 0, validated.stdout + validated.stderr)
            record = json.loads(target.read_text(encoding="utf-8"))
            self.assertNotIn("222", record["actor_id"])
            self.assertNotIn('"actor_id"', record["identity_claim"])
            claim = json.loads(record["identity_claim"])
            claim["actor_ref"] = "ghoidc-v1:" + "f" * 64
            record["identity_claim"] = json.dumps(claim, separators=(",", ":"))
            target.write_text(json.dumps(record), encoding="utf-8")
            rejected = subprocess.run(
                [sys.executable, str(root / "scripts/validate_enterprise.py")],
                cwd=root, text=True, capture_output=True,
            )
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("invalid github-oidc identity contract", rejected.stdout)

    def test_malicious_dispatch_inputs_are_rejected_without_output(self):
        with tempfile.TemporaryDirectory(prefix="sdd-input-") as base:
            root = Path(base) / "kit"
            shutil.copytree(SOURCE, root, ignore=shutil.ignore_patterns("__pycache__", "dist"))
            env = self.trusted_env()
            env.update({
                "SDD_CHANGE_INPUT": "CHG-2026-003;echo-pwned",
                "SDD_GATE_INPUT": "G4_READY",
                "SDD_EVIDENCE_IDS_INPUT": "EVD-G4-IMPLEMENTATION-READINESS",
                "SDD_ACTOR_ID": "ghoidc-v1:" + "0" * 64,
                "SDD_ACTOR_ROLE": "engineering_lead",
                "SDD_IDENTITY_PROVIDER": "github-oidc",
                "SDD_IDENTITY_CLAIM": "{}",
                "SDD_COMMIT_SHA": "a" * 40,
            })
            result = subprocess.run(
                [sys.executable, str(root / "scripts/create_approval.py"), "--from-env"],
                cwd=root, env=env, text=True, capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            approvals = root / "changes/CHG-2026-003-private-gate-role-injection/approvals"
            self.assertFalse(list(approvals.glob("*.json")))

    def test_workflow_has_step_scoped_secrets_cleanup_and_exact_artifact(self):
        workflow = (SOURCE / ".github/workflows/sdd-gate-approval.yml").read_text(encoding="utf-8")
        self.assertEqual(workflow.count("secrets.SDD_GITHUB_ROLE_MAP_JSON"), 1)
        self.assertEqual(workflow.count("secrets.SDD_IDENTITY_PEPPER_B64"), 1)
        self.assertNotIn("github.actor }}", workflow)
        self.assertNotIn("config/github-role-map.json", workflow)
        self.assertIn("if: always()", workflow)
        self.assertIn("path: ${{ steps.approval.outputs.path }}", workflow)
        self.assertNotIn("path: changes/*/approvals/*.json", workflow)
        run_lines = [line for line in workflow.splitlines() if line.lstrip().startswith(("run:", "python ", "approval_path="))]
        self.assertFalse(any("${{ inputs." in line for line in run_lines))


if __name__ == "__main__":
    unittest.main()
