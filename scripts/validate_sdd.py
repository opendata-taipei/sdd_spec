#!/usr/bin/env python3
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "proposal.md", "requirements.md", "nfr.md", "design.md", "tasks.md",
    "test-plan.md", "release-plan.md", "closure-report.md", "manifest.yaml", "state.json"
]
REQ_RE = re.compile(r"\b(?:REQ|NFR|SEC|DATA|OPS)-[A-Z0-9-]+-\d{3,}\b")
TASK_RE = re.compile(r"\bTASK-\d{3,}\b")
TEST_RE = re.compile(r"\bTEST-[A-Z0-9-]+-\d{3,}\b")
ALLOWED_STATES = {
    "DRAFT","PROPOSAL_REVIEW","REQUIREMENTS_REVIEW","DESIGN_REVIEW",
    "READY_FOR_IMPLEMENTATION","IMPLEMENTING","VERIFYING","RELEASE_READY",
    "RELEASING","MONITORING","CLOSED","BLOCKED","REJECTED","ROLLED_BACK","CANCELLED"
}
errors, warnings = [], []

for d in sorted((ROOT / "changes").iterdir()):
    if not d.is_dir() or d.name.startswith("_"):
        continue
    missing = [f for f in REQUIRED if not (d / f).exists()]
    if missing:
        errors.append(f"{d.name}: missing {', '.join(missing)}")
        continue
    try:
        state = json.loads((d / "state.json").read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{d.name}: invalid state.json: {exc}")
        continue
    if state.get("status") not in ALLOWED_STATES:
        errors.append(f"{d.name}: invalid status {state.get('status')}")
    docs = "\n".join((d / f).read_text(encoding="utf-8") for f in ["requirements.md","nfr.md","design.md","tasks.md","test-plan.md"])
    reqs = set(REQ_RE.findall((d / "requirements.md").read_text(encoding="utf-8") + "\n" + (d / "nfr.md").read_text(encoding="utf-8")))
    tasks = set(TASK_RE.findall((d / "tasks.md").read_text(encoding="utf-8")))
    tests = set(TEST_RE.findall((d / "test-plan.md").read_text(encoding="utf-8")))
    if not reqs:
        warnings.append(f"{d.name}: no valid Requirement IDs found")
    if not tasks:
        warnings.append(f"{d.name}: no Task IDs found")
    if not tests:
        warnings.append(f"{d.name}: no Test IDs found")
    tasks_text = (d / "tasks.md").read_text(encoding="utf-8")
    tests_text = (d / "test-plan.md").read_text(encoding="utf-8")
    for req in sorted(reqs):
        if req not in tasks_text:
            warnings.append(f"{d.name}: {req} not referenced by tasks.md")
        if req not in tests_text:
            warnings.append(f"{d.name}: {req} not referenced by test-plan.md")

for w in warnings:
    print("WARNING:", w)
for e in errors:
    print("ERROR:", e)
print(f"Validation complete: {len(errors)} error(s), {len(warnings)} warning(s)")
sys.exit(1 if errors else 0)
