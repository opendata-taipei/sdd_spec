#!/usr/bin/env python3
from __future__ import annotations
import json
import re
import shutil
import sys
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from event_store import canonical_hash

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "changes" / "_template"


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(2)

if len(sys.argv) != 4:
    fail("Usage: python scripts/bootstrap_change.py CHG-2026-001 add-feature github-login-or-corporate-id")

change_id, slug, author = sys.argv[1], sys.argv[2], sys.argv[3]
if not re.fullmatch(r"CHG-\d{4}-\d{3,}", change_id):
    fail("Change ID must match CHG-YYYY-NNN")
if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
    fail("Slug must use lowercase kebab-case")

target = ROOT / "changes" / f"{change_id}-{slug}"
if target.exists():
    fail(f"Target already exists: {target}")
shutil.copytree(TEMPLATE, target)
title = slug.replace("-", " ").title()
for p in target.iterdir():
    if p.suffix in {".md", ".yaml", ".yml", ".json"}:
        text = p.read_text(encoding="utf-8")
        text = text.replace("{{CHANGE_ID}}", change_id).replace("{{TITLE}}", title).replace("REPLACE_ME", author)
        p.write_text(text, encoding="utf-8")
state_path = target / "state.json"
state = json.loads(state_path.read_text(encoding="utf-8"))
state["change_id"] = change_id
state["title"] = title
state["updated_by"] = author
state["updated_at"] = datetime.now(timezone(timedelta(hours=8))).isoformat()
state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
event = {
    "event_id": "EVT-" + uuid.uuid4().hex.upper(), "change_id": change_id,
    "sequence": 1, "event_type": "STATE_SNAPSHOT", "occurred_at": state["updated_at"],
    "actor_id": author, "actor_role": "change_author", "payload": {"state": state},
    "previous_hash": None, "commit_sha": None,
}
event["event_hash"] = canonical_hash(event)
(target / "events.jsonl").write_text(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
print(target.relative_to(ROOT))
