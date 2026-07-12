#!/usr/bin/env python3
from __future__ import annotations
import argparse
import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from event_store import canonical_hash, read_events, verify_chain

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description="Promote a completed Agent Run to SDD Evidence")
parser.add_argument("--run", required=True)
parser.add_argument("--change", required=True)
args = parser.parse_args()
run_dir = ROOT / "reports" / "runs" / args.run
run_path = run_dir / "run.json"
run = json.loads(run_path.read_text(encoding="utf-8"))
if run.get("status") not in {"completed", "escalated", "blocked"}:
    raise SystemExit("Only terminal Agent Runs can become evidence")
if run.get("change_id") != args.change:
    raise SystemExit("Agent Run belongs to a different change")
matches = [p for p in (ROOT / "changes").glob(args.change + "*") if p.is_dir()]
if len(matches) != 1: raise SystemExit(f"Expected one change directory, found {len(matches)}")
evidence_id = "EVD-AGENT-" + args.run.removeprefix("RUN-")
record = {"evidence_id": evidence_id, "change_id": args.change, "type": "test",
          "uri": str(run_path.relative_to(ROOT)).replace("\\", "/"),
          "sha256": hashlib.sha256(run_path.read_bytes()).hexdigest(), "produced_at": run["ended_at"],
          "producer": run["agent_id"], "tool": {"name": "agent-runtime-audit", "version": "1.0"},
          "requirements": [], "result": "pass" if run["status"] == "completed" else "informational"}
target = matches[0] / "evidence" / f"{evidence_id}.json"
if target.exists(): raise SystemExit("Evidence already exists")
events_path = matches[0] / "events.jsonl"
events = read_events(events_path)
chain_errors = verify_chain(events)
if chain_errors: raise SystemExit("Invalid event chain: " + "; ".join(chain_errors))
target.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
event = {"event_id": "EVT-" + uuid.uuid4().hex.upper(), "change_id": args.change,
         "sequence": len(events) + 1, "event_type": "EVIDENCE_ADDED",
         "occurred_at": datetime.now(timezone.utc).isoformat(), "actor_id": run["agent_id"],
         "actor_role": "evidence_producer", "payload": {"evidence_id": evidence_id, "run_id": args.run},
         "previous_hash": events[-1]["event_hash"] if events else None, "commit_sha": None}
event["event_hash"] = canonical_hash(event)
with events_path.open("a", encoding="utf-8", newline="\n") as handle:
    handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
print(target.relative_to(ROOT))
