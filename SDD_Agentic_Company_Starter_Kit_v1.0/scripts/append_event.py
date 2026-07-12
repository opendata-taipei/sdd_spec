#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from event_store import canonical_hash, read_events, verify_chain

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--change", required=True)
parser.add_argument("--type", required=True)
parser.add_argument("--payload", required=True, help="JSON object")
args = parser.parse_args()
actor = os.environ.get("SDD_ACTOR_ID")
role = os.environ.get("SDD_ACTOR_ROLE")
commit = os.environ.get("SDD_COMMIT_SHA")
if not actor or not role:
    raise SystemExit("SDD_ACTOR_ID and SDD_ACTOR_ROLE are required")
if commit and not re.fullmatch(r"[a-fA-F0-9]{40}", commit):
    raise SystemExit("SDD_COMMIT_SHA must be a full Git SHA")
payload = json.loads(args.payload)
if not isinstance(payload, dict):
    raise SystemExit("payload must be a JSON object")
matches = [p for p in (ROOT / "changes").glob(args.change + "*") if p.is_dir()]
if len(matches) != 1:
    raise SystemExit(f"Expected one change directory, found {len(matches)}")
path = matches[0] / "events.jsonl"
events = read_events(path)
chain_errors = verify_chain(events)
if chain_errors:
    raise SystemExit("Existing event chain is invalid: " + "; ".join(chain_errors))
event = {
    "event_id": "EVT-" + uuid.uuid4().hex.upper(), "change_id": args.change,
    "sequence": len(events) + 1, "event_type": args.type,
    "occurred_at": datetime.now(timezone.utc).isoformat(), "actor_id": actor,
    "actor_role": role, "payload": payload,
    "previous_hash": events[-1]["event_hash"] if events else None, "commit_sha": commit,
}
event["event_hash"] = canonical_hash(event)
with path.open("a", encoding="utf-8", newline="\n") as handle:
    handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
print(f"{path.relative_to(ROOT)}#{event['sequence']} {event['event_hash']}")
