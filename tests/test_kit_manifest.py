from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]
SCRIPT = SOURCE / "scripts" / "build_kit_manifest.py"


def load_manifest_module():
    spec = importlib.util.spec_from_file_location("build_kit_manifest", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class KitManifestTests(unittest.TestCase):
    def run_script(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(root / "scripts" / "build_kit_manifest.py"), *args],
            cwd=root,
            text=True,
            capture_output=True,
        )

    def fixture(self, base: Path) -> Path:
        root = base / "kit"
        (root / "scripts").mkdir(parents=True)
        shutil.copy2(SCRIPT, root / "scripts" / SCRIPT.name)
        (root / "README.md").write_text("fixture\n", encoding="utf-8")
        (root / "KIT_MANIFEST.json").write_text("{}\n", encoding="utf-8")
        return root

    def test_current_manifest_is_valid_and_check_is_read_only(self):
        before = (SOURCE / "KIT_MANIFEST.json").read_bytes()
        started = time.perf_counter()
        result = self.run_script(SOURCE, "--check")
        duration = time.perf_counter() - started
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertLess(duration, 5.0)
        self.assertEqual((SOURCE / "KIT_MANIFEST.json").read_bytes(), before)

    def test_unmanaged_file_makes_check_fail(self):
        with tempfile.TemporaryDirectory(prefix="sdd-manifest-test-") as base:
            root = self.fixture(Path(base))
            self.assertEqual(self.run_script(root).returncode, 0)
            (root / "unexpected.txt").write_text("drift\n", encoding="utf-8")
            result = self.run_script(root, "--check")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("run scripts/build_kit_manifest.py", result.stdout)

    def test_runtime_outputs_are_excluded(self):
        with tempfile.TemporaryDirectory(prefix="sdd-manifest-test-") as base:
            root = self.fixture(Path(base))
            runtime_files = (
                "reports/evals/latest.json",
                "reports/runs/RUN-TEST/run.json",
                "reports/test-fixture/result.json",
                "reports/promotion-test-fixture/result.json",
            )
            for relative in runtime_files:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("{}\n", encoding="utf-8")
            self.assertEqual(self.run_script(root).returncode, 0)
            manifest = json.loads((root / "KIT_MANIFEST.json").read_text(encoding="utf-8"))
            self.assertTrue(set(runtime_files).isdisjoint(manifest["files"]))
            self.assertEqual(self.run_script(root, "--check").returncode, 0)

    def test_sorting_has_case_sensitive_tie_breaker(self):
        module = load_manifest_module()
        values = ["z.txt", "A.txt", "a.txt", "B.txt"]
        self.assertEqual(
            sorted(values, key=module.manifest_sort_key),
            ["A.txt", "a.txt", "B.txt", "z.txt"],
        )

    def test_public_role_map_contains_no_email_or_github_token(self):
        text = (SOURCE / "config" / "github-role-map.json").read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text))
        self.assertIsNone(re.search(r"gh[pousr]_[A-Za-z0-9_]{20,}", text))
        self.assertIn("REPLACE_WITH_GITHUB_LOGIN", text)


if __name__ == "__main__":
    unittest.main()
