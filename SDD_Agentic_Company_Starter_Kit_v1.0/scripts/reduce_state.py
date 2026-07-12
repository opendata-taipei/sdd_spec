#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
from pathlib import Path
from event_store import read_events, reduce_events, verify_chain

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--change", required=True)
parser.add_argument("--check", action="store_true", help="Compare reduced state with state.json without writing")
args = parser.parse_args()
matches = [p for p in (ROOT / "changes").glob(args.change + "*") if p.is_dir()]
if len(matches) != 1:
    raise SystemExit(f"Expected one change directory, found {len(matches)}")
change = matches[0]
events = read_events(change / "events.jsonl")
errors = verify_chain(events)
if errors:
    raise SystemExit("Invalid event chain: " + "; ".join(errors))
reduced = reduce_events(events)
state_path = change / "state.json"
if args.check:
    current = json.loads(state_path.read_text(encoding="utf-8"))
    if reduced != current:
        raise SystemExit("state.json differs from event-derived state")
    print("Event-derived state matches state.json")
else:
    state_path.write_text(json.dumps(reduced, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(state_path.relative_to(ROOT))
