from __future__ import annotations
import json
import shutil
import subprocess
import sys
import unittest
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from runtime_audit import AuditRun, redact

class RuntimeAuditTests(unittest.TestCase):
    def test_redacts_common_secrets_and_pii(self):
        value = redact({"api_key": "sk-abcdefghijklmnop", "message": "Authorization: Bearer abc123 user@example.com"})
        rendered = json.dumps(value)
        self.assertNotIn("abcdefghijklmnop", rendered)
        self.assertNotIn("abc123", rendered)
        self.assertNotIn("user@example.com", rendered)

    def test_writes_complete_audit_bundle(self):
        runs = ROOT / "reports" / "runs"
        audit = AuditRun(ROOT, "CHG-EXAMPLE-001", "test-agent", "reference", "test-model", "1.0",
                         [ROOT / "evals/datasets/governance-baseline.jsonl"])
        try:
            audit.record_tool("test-tool", "test", "allowed", {"password": "do-not-store"}, {"ok": True}, 1)
            audit.record_guardrail("secret-check", "passed", "sk-abcdefghijklmnop", "no leak")
            audit.finalize("completed", {"email": "user@example.com"})
            for name in ("run.json", "context-manifest.json", "tool-events.jsonl", "guardrail-events.jsonl", "final-output.json"):
                self.assertTrue((audit.dir / name).is_file())
            all_text = "".join(p.read_text(encoding="utf-8") for p in audit.dir.iterdir() if p.is_file())
            self.assertNotIn("do-not-store", all_text)
            self.assertNotIn("abcdefghijklmnop", all_text)
            self.assertNotIn("user@example.com", all_text)
        finally:
            shutil.rmtree(audit.dir, ignore_errors=True)
            if runs.exists() and not any(runs.iterdir()): runs.rmdir()

    def test_evidence_promotion_appends_event(self):
        base = ROOT / "reports" / f"promotion-test-{uuid.uuid4().hex}"
        copy = base / "kit"
        base.mkdir(parents=True)
        shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns("reports", "__pycache__"))
        sys.path.insert(0, str(copy / "scripts"))
        try:
            audit = AuditRun(copy, "CHG-EXAMPLE-001", "test-agent", "reference", "test", "1.0",
                             [copy / "evals/datasets/governance-baseline.jsonl"])
            audit.finalize("completed", {"passed": True})
            event_path = copy / "changes/CHG-EXAMPLE-001-add-account-lockout/events.jsonl"
            before = len(event_path.read_text(encoding="utf-8").splitlines())
            result = subprocess.run([sys.executable, str(copy / "scripts/run_to_evidence.py"),
                                     "--run", audit.run_id, "--change", "CHG-EXAMPLE-001"],
                                    cwd=copy, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            after = len(event_path.read_text(encoding="utf-8").splitlines())
            self.assertEqual(after, before + 1)
            self.assertIn('"event_type": "EVIDENCE_ADDED"', event_path.read_text(encoding="utf-8"))
        finally:
            shutil.rmtree(base, ignore_errors=True)
