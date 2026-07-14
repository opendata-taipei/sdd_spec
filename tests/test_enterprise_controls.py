from __future__ import annotations
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from event_store import canonical_hash, reduce_events

SOURCE = Path(__file__).resolve().parents[1]
CHANGE = "changes/CHG-EXAMPLE-001-add-account-lockout"

class EnterpriseControlTests(unittest.TestCase):
    @contextmanager
    def fixture(self):
        with tempfile.TemporaryDirectory(prefix="sdd-enterprise-test-") as base:
            target = Path(base) / "kit"
            shutil.copytree(
                SOURCE,
                target,
                ignore=shutil.ignore_patterns(
                    "__pycache__", "runs", "test-*", "promotion-test-*", "latest.json"
                ),
            )
            yield target

    def validate(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(root / "scripts/validate_enterprise.py")],
                              cwd=root, text=True, capture_output=True)

    def test_gate_is_derived_from_approvals(self):
        with self.fixture() as root:
            (root / CHANGE / "approvals/APR-G3-ARCHITECT.json").unlink()
            result = self.validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("requires approved G3_DESIGN", result.stdout)

    def test_text_evidence_hash_is_line_ending_stable(self):
        with self.fixture() as root:
            path = root / CHANGE / "proposal.md"
            content = path.read_text(encoding="utf-8").replace("\r\n", "\n")
            path.write_bytes(content.replace("\n", "\r\n").encode("utf-8"))
            result = self.validate(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_untrusted_identity_is_rejected(self):
        with self.fixture() as root:
            path = root / CHANGE / "approvals/APR-G3-ARCHITECT.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["identity_provider"] = "untrusted-idp"
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            result = self.validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("untrusted identity provider", result.stdout)

    def test_high_risk_author_cannot_approve(self):
        with self.fixture() as root:
            manifest_path = root / CHANGE / "manifest.yaml"
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            manifest["risk_level"] = "L4"
            manifest["authors"] = ["example-product-owner"]
            manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), encoding="utf-8")
            state_path = root / CHANGE / "state.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["risk_level"] = "L4"
            state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
            result = self.validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("cannot approve high-risk change", result.stdout)

    def test_event_chain_tampering_is_rejected(self):
        with self.fixture() as root:
            path = root / CHANGE / "events.jsonl"
            event = json.loads(path.read_text(encoding="utf-8"))
            event["actor_id"] = "tampered-actor"
            path.write_text(json.dumps(event), encoding="utf-8")
            result = self.validate(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("event_hash mismatch", result.stdout)

    def test_bootstrap_initializes_event_store(self):
        with self.fixture() as root:
            result = subprocess.run([sys.executable, str(root / "scripts/bootstrap_change.py"),
                                     "CHG-2026-999", "bootstrap-test", "test-author"],
                                    cwd=root, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            change = root / "changes/CHG-2026-999-bootstrap-test"
            self.assertTrue((change / "events.jsonl").is_file())
            check = subprocess.run([sys.executable, str(root / "scripts/reduce_state.py"),
                                    "--change", "CHG-2026-999", "--check"],
                                   cwd=root, text=True, capture_output=True)
            self.assertEqual(check.returncode, 0, check.stderr)

    def test_remediation_reason_is_projected_without_changing_old_events(self):
        snapshot = {
            "event_type": "STATE_SNAPSHOT", "actor_id": "author", "actor_role": "change_author",
            "occurred_at": "2026-01-01T00:00:00Z",
            "payload": {"state": {"status": "DRAFT", "current_phase": "PROPOSAL", "decisions": []}},
        }
        transition = {
            "event_type": "STATE_TRANSITIONED", "actor_id": "manager", "actor_role": "release_manager",
            "occurred_at": "2026-01-02T00:00:00Z",
            "payload": {
                "from": "DRAFT", "to": "PROPOSAL_REVIEW", "evidence": "EVD-REMEDIATION",
                "reason": "retrospective_governance_remediation",
            },
        }
        state = reduce_events([snapshot, transition])
        self.assertEqual(state["decisions"][0]["reason"], "retrospective_governance_remediation")

if __name__ == "__main__":
    unittest.main()
