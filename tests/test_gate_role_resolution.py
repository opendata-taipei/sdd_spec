from __future__ import annotations

import json
import os
import ctypes
import statistics
import subprocess
import sys
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from gate_identity import GateIdentityError, load_protected_role_map, resolve_gate_role

POLICY = json.loads((ROOT / "config/enterprise-policy.json").read_text(encoding="utf-8"))
ALLOWED = set(POLICY["allowed_roles"])


def peak_rss_bytes() -> int:
    if os.name == "nt":
        class ProcessMemoryCounters(ctypes.Structure):
            _fields_ = [
                ("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong),
                ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t),
            ]
        counters = ProcessMemoryCounters()
        counters.cb = ctypes.sizeof(counters)
        get_current_process = ctypes.windll.kernel32.GetCurrentProcess
        get_current_process.restype = ctypes.c_void_p
        get_process_memory_info = ctypes.windll.psapi.GetProcessMemoryInfo
        get_process_memory_info.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong]
        get_process_memory_info.restype = ctypes.c_int
        if not get_process_memory_info(get_current_process(), ctypes.byref(counters), counters.cb):
            raise OSError("GetProcessMemoryInfo failed")
        return int(counters.PeakWorkingSetSize)
    import resource
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(usage if sys.platform == "darwin" else usage * 1024)


class GateRoleResolutionTests(unittest.TestCase):
    def test_valid_mapping_and_unique_role(self):
        raw = json.dumps({"schema_version": "1.0", "actors": {"123": ["product_owner", "architect"]}})
        mapping = load_protected_role_map(raw, ALLOWED)
        self.assertEqual(resolve_gate_role(mapping, "123", "G3_DESIGN", POLICY), "architect")
        env = os.environ.copy()
        env["SDD_GITHUB_ROLE_MAP_JSON"] = raw
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/resolve_github_role.py"),
             "--actor-id", "123", "--gate", "G3_DESIGN"],
            cwd=ROOT, env=env, text=True, capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "architect\n")
        self.assertEqual(result.stderr, "")

    def test_contract_failures_are_rejected(self):
        invalid = [
            "",
            "{",
            '{"schema_version":"1.0","schema_version":"1.0","actors":{}}',
            '{"schema_version":"1.0","actors":{"123":["architect"],"123":["architect"]}}',
            json.dumps({"schema_version": "1.0", "actors": {}, "extra": True}),
            json.dumps({"schema_version": "2.0", "actors": {}}),
            json.dumps({"schema_version": "1.0", "actors": {"0123": ["architect"]}}),
            json.dumps({"schema_version": "1.0", "actors": {"123": []}}),
            json.dumps({"schema_version": "1.0", "actors": {"123": ["architect", "architect"]}}),
            json.dumps({"schema_version": "1.0", "actors": {"123": ["unknown"]}}),
            " " * (32 * 1024 + 1),
        ]
        for raw in invalid:
            with self.subTest(raw=raw[:80]):
                with self.assertRaises(GateIdentityError):
                    load_protected_role_map(raw, ALLOWED)
        too_many = {str(index + 1): ["architect"] for index in range(1001)}
        with self.assertRaises(GateIdentityError):
            load_protected_role_map(json.dumps({"schema_version": "1.0", "actors": too_many}), ALLOWED)

    def test_resolution_failures_do_not_reveal_mapping(self):
        marker = "98765432101234567890"
        raw = json.dumps({
            "schema_version": "1.0",
            "actors": {
                "123": ["product_owner", "architect"],
                marker: ["architect"],
                "456": ["engineering_lead", "qa_lead"],
            },
        })
        env = os.environ.copy()
        env["SDD_GITHUB_ROLE_MAP_JSON"] = raw
        cases = [
            ["--actor-id", "999", "--gate", "G3_DESIGN"],
            ["--actor-id", "123", "--gate", "G9_UNKNOWN"],
            ["--actor-id", "123", "--gate", "G4_READY"],
            ["--actor-id", "456", "--gate", "G5_IMPLEMENTATION"],
        ]
        for arguments in cases:
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/resolve_github_role.py"), *arguments],
                cwd=ROOT, env=env, text=True, capture_output=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertNotIn(marker, result.stderr)
            self.assertNotIn(raw, result.stderr)

    def test_cli_requires_protected_mapping_and_has_no_public_fallback(self):
        env = os.environ.copy()
        env.pop("SDD_GITHUB_ROLE_MAP_JSON", None)
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/resolve_github_role.py"),
             "--actor-id", "123", "--gate", "G3_DESIGN"],
            cwd=ROOT, env=env, text=True, capture_output=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    def test_maximum_fixture_p95_is_below_threshold(self):
        actors = {str(index + 1): ["product_owner", "architect"] for index in range(850)}
        raw = json.dumps({"schema_version": "1.0", "actors": actors}, separators=(",", ":"))
        raw += " " * (32 * 1024 - len(raw.encode("utf-8")))
        self.assertEqual(len(raw.encode("utf-8")), 32 * 1024)
        durations = []
        for _ in range(100):
            started = time.perf_counter()
            mapping = load_protected_role_map(raw, ALLOWED)
            resolve_gate_role(mapping, "850", "G3_DESIGN", POLICY)
            durations.append(time.perf_counter() - started)
        p95 = statistics.quantiles(durations, n=100, method="inclusive")[94]
        self.assertLess(p95, 0.2, f"p95={p95:.6f}s")
        self.assertLess(peak_rss_bytes(), 64 * 1024 * 1024)


if __name__ == "__main__":
    unittest.main()
