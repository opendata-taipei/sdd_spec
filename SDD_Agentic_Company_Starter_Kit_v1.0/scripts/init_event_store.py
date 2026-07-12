#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from event_store import canonical_hash

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--change", required=True)
args = parser.parse_args()
matches = [p for p in (ROOT / "changes").glob(args.change + "*") if p.is_dir()]
if len(matches) != 1:
    raise SystemExit(f"Expected one change directory, found {len(matches)}")
change = matches[0]
target = change / "events.jsonl"
if target.exists() and target.stat().st_size:
    raise SystemExit("Event store already initialized")
state = json.loads((change / "state.json").read_text(encoding="utf-8"))
event = {
    "event_id": "EVT-" + uuid.uuid4().hex.upper(), "change_id": state["change_id"],
    "sequence": 1, "event_type": "STATE_SNAPSHOT",
    "occurred_at": datetime.now(timezone.utc).isoformat(),
    "actor_id": os.environ.get("SDD_ACTOR_ID", "migration-tool"),
    "actor_role": os.environ.get("SDD_ACTOR_ROLE", "change_manager"),
    "payload": {"state": state}, "previous_hash": None,
    "commit_sha": os.environ.get("SDD_COMMIT_SHA"),
}
event["event_hash"] = canonical_hash(event)
target.write_text(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
print(target.relative_to(ROOT))
