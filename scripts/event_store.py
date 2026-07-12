from __future__ import annotations
import hashlib
import json
from pathlib import Path

def canonical_hash(event: dict) -> str:
    unsigned = {k: v for k, v in event.items() if k != "event_hash"}
    raw = json.dumps(unsigned, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def read_events(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

def verify_chain(events: list[dict]) -> list[str]:
    errors = []
    previous = None
    for index, event in enumerate(events, 1):
        if event.get("sequence") != index:
            errors.append(f"event {index}: sequence mismatch")
        if event.get("previous_hash") != previous:
            errors.append(f"event {index}: previous_hash mismatch")
        actual = canonical_hash(event)
        if event.get("event_hash") != actual:
            errors.append(f"event {index}: event_hash mismatch")
        previous = event.get("event_hash")
    return errors

def reduce_events(events: list[dict]) -> dict:
    state: dict = {}
    for event in events:
        payload = event.get("payload", {})
        kind = event.get("event_type")
        if kind == "STATE_SNAPSHOT":
            state = dict(payload.get("state", {}))
        elif kind == "STATE_TRANSITIONED":
            state["status"] = payload["to"]
            state["current_phase"] = payload["to"]
            state["updated_by"] = event["actor_id"]
            state["updated_at"] = event["occurred_at"]
            state.setdefault("decisions", []).append({
                "type": "state_transition", "from": payload["from"], "to": payload["to"],
                "actor": event["actor_id"], "actor_role": event["actor_role"],
                "evidence": payload.get("evidence")
            })
        elif kind == "RISK_CHANGED":
            state["risk_level"] = payload["to"]
        elif kind == "CHANGE_CLOSED":
            state["status"] = "CLOSED"
            state["current_phase"] = "CLOSED"
    return state
