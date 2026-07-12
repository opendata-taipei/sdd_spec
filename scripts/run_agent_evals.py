#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from runtime_audit import AuditRun

ROOT = Path(__file__).resolve().parents[1]

def load_cases() -> list[dict]:
    cases = []
    for path in sorted((ROOT / "evals" / "datasets").glob("*.jsonl")):
        cases.extend(json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    return cases

parser = argparse.ArgumentParser(description="Run vendor-neutral governance evals against an agent adapter")
parser.add_argument("--adapter-command", help="Adapter command line; defaults to the bundled reference adapter")
parser.add_argument("--adapter-id", default="reference-policy-1.0")
parser.add_argument("--report", default=str(ROOT / "reports" / "evals" / "latest.json"))
parser.add_argument("--change-id", default="CHG-EXAMPLE-001")
args = parser.parse_args()
cases = load_cases()
if not cases:
    raise SystemExit("No eval cases found")

if args.adapter_command:
    command = [part.strip('"') for part in shlex.split(args.adapter_command, posix=False)]
else:
    command = [sys.executable, str(ROOT / "evals" / "adapters" / "reference_adapter.py")]
context_sources = sorted((ROOT / "evals" / "datasets").glob("*.jsonl"))
audit = AuditRun(ROOT, args.change_id, "governance-eval-agent", args.adapter_id.split("-", 1)[0],
                 args.adapter_id, "eval-contract-1.0", context_sources)
started = datetime.now(timezone.utc)
proc = subprocess.Popen(command, cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE, text=True, encoding="utf-8")
assert proc.stdin and proc.stdout
for case in cases:
    proc.stdin.write(json.dumps(case, ensure_ascii=False) + "\n")
proc.stdin.close()

outputs: dict[str, dict] = {}
parse_errors = []
for line in proc.stdout:
    try:
        item = json.loads(line)
        outputs[item["case_id"]] = item
    except Exception as exc:
        parse_errors.append(f"invalid adapter output: {exc}: {line.strip()}")
stderr = proc.stderr.read() if proc.stderr else ""
return_code = proc.wait(timeout=60)
duration_ms = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)
audit.record_tool("agent-adapter", "governance-eval", "allowed" if return_code == 0 else "failed",
                  {"case_ids": [c["case_id"] for c in cases]}, {"output_case_ids": sorted(outputs)}, duration_ms,
                  stderr.strip() or None)

results = []
for case in cases:
    output = outputs.get(case["case_id"])
    passed = bool(output and output.get("decision") == case["expected"])
    results.append({
        "case_id": case["case_id"], "category": case["category"],
        "expected": case["expected"], "actual": output.get("decision") if output else None,
        "passed": passed, "output": output,
    })
passed_count = sum(1 for r in results if r["passed"])
for result in results:
    audit.record_guardrail(result["category"], "passed" if result["passed"] else "failed",
                           result["output"], f"expected={result['expected']}; actual={result['actual']}")
report = {
    "schema_version": "1.0", "adapter_id": args.adapter_id,
    "executed_at": datetime.now(timezone.utc).isoformat(),
    "summary": {"total": len(results), "passed": passed_count, "failed": len(results) - passed_count},
    "results": results, "adapter_errors": parse_errors + ([stderr.strip()] if stderr.strip() else []),
}
report_path = Path(args.report)
report_path.parent.mkdir(parents=True, exist_ok=True)
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
audit.finalize("completed" if return_code == 0 and not parse_errors and passed_count == len(results) else "failed",
               report, {"required": any(r["actual"] == "escalate" for r in results)},
               {"input_tokens": 0, "output_tokens": 0, "cost_usd": 0})
print(f"Agent evals: {passed_count}/{len(results)} passed; report={report_path}")
print(f"Runtime audit: {audit.dir.relative_to(ROOT)}")
if return_code != 0:
    print(f"ERROR: adapter exited with {return_code}")
sys.exit(1 if return_code != 0 or parse_errors or passed_count != len(results) else 0)
