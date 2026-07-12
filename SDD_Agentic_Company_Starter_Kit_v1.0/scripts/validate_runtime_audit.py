#!/usr/bin/env python3
from __future__ import annotations
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = {
    "run.json": "agent-run.schema.json",
    "context-manifest.json": "context-manifest.schema.json",
}
errors = []
run_count = 0

def validate(record, schema_name, source):
    schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
    for issue in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(record):
        errors.append(f"{source}:{'.'.join(map(str, issue.absolute_path)) or '$'}: {issue.message}")

for run_dir in sorted((ROOT / "reports" / "runs").glob("RUN-*")) if (ROOT / "reports" / "runs").exists() else []:
    run_count += 1
    for filename, schema in SCHEMAS.items():
        path = run_dir / filename
        if not path.exists(): errors.append(f"{run_dir.name}: missing {filename}"); continue
        validate(json.loads(path.read_text(encoding="utf-8")), schema, path.relative_to(ROOT))
    for filename, schema in (("tool-events.jsonl", "tool-event.schema.json"), ("guardrail-events.jsonl", "guardrail-event.schema.json")):
        path = run_dir / filename
        if not path.exists(): errors.append(f"{run_dir.name}: missing {filename}"); continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip(): validate(json.loads(line), schema, f"{path.relative_to(ROOT)}:{number}")
    if not (run_dir / "final-output.json").exists(): errors.append(f"{run_dir.name}: missing final-output.json")
for error in errors: print("ERROR:", error)
print(f"Runtime audit validation: {run_count} run(s), {len(errors)} error(s)")
sys.exit(1 if errors else 0)
