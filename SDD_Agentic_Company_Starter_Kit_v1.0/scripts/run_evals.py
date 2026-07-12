#!/usr/bin/env python3
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {"case_id", "category", "input", "expected", "tags"}
allowed = {"allow", "block", "refuse", "escalate"}
errors = []
count = 0
for path in sorted((ROOT / "evals" / "datasets").glob("*.jsonl")):
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        count += 1
        try:
            case = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}:{line_no}: invalid JSON: {exc}")
            continue
        missing = REQUIRED - case.keys()
        if missing:
            errors.append(f"{path.name}:{line_no}: missing {sorted(missing)}")
        if case.get("expected") not in allowed:
            errors.append(f"{path.name}:{line_no}: invalid expected decision")
if count == 0:
    errors.append("no eval cases found")
for error in errors:
    print("ERROR:", error)
print(f"Eval baseline validation: {count} case(s), {len(errors)} error(s)")
sys.exit(1 if errors else 0)
