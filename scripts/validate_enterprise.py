#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path
from event_store import read_events, reduce_events, verify_chain

try:
    import yaml
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError as exc:
    raise SystemExit("Missing governance dependencies. Run: python -m pip install -r requirements-governance.txt") from exc

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / "config" / "enterprise-policy.json").read_text(encoding="utf-8"))
errors: list[str] = []
warnings: list[str] = []

TEXT_EVIDENCE_SUFFIXES = {
    ".csv", ".json", ".jsonl", ".md", ".txt", ".yaml", ".yml",
}

def evidence_sha256(path: Path) -> str:
    content = path.read_bytes()
    if path.suffix.lower() in TEXT_EVIDENCE_SUFFIXES:
        content = content.replace(b"\r\n", b"\n")
    return hashlib.sha256(content).hexdigest()

def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
        return {}

def validate_schema(record: dict, schema_name: str, source: Path) -> None:
    schema = load_json(ROOT / "schemas" / schema_name)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for issue in sorted(validator.iter_errors(record), key=lambda e: list(e.absolute_path)):
        location = ".".join(str(x) for x in issue.absolute_path) or "$"
        errors.append(f"{source.relative_to(ROOT)}:{location}: {issue.message}")

def derived_gates(approvals: dict[str, list[dict]]) -> dict[str, str]:
    result = {}
    for gate, rule in POLICY["gate_policy"].items():
        actors = {a.get("actor_id") for a in approvals.get(gate, []) if a.get("decision") == "approved"}
        result[gate] = "approved" if len(actors) >= rule["min_approvals"] else "pending"
    return result

for change_dir in sorted((ROOT / "changes").iterdir()):
    if not change_dir.is_dir() or change_dir.name.startswith("_"):
        continue
    state_path = change_dir / "state.json"
    manifest_path = change_dir / "manifest.yaml"
    state = load_json(state_path)
    validate_schema(state, "change-state.schema.json", state_path)
    event_path = change_dir / "events.jsonl"
    events = read_events(event_path)
    if not events:
        errors.append(f"{change_dir.name}: append-only event store is not initialized")
    else:
        for index, event in enumerate(events, 1):
            validate_schema(event, "change-event.schema.json", event_path)
            if event.get("change_id") != state.get("change_id"):
                errors.append(f"{change_dir.name}: event {index} belongs to another change")
        errors.extend(f"{change_dir.name}: {message}" for message in verify_chain(events))
        if reduce_events(events) != state:
            errors.append(f"{change_dir.name}: state.json differs from event-derived state")
    try:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        errors.append(f"{change_dir.name}: invalid manifest YAML: {exc}")
        continue
    if not isinstance(manifest, dict):
        errors.append(f"{change_dir.name}: manifest must be a mapping")
        continue
    if "status" in manifest or "quality_gates" in manifest:
        errors.append(f"{change_dir.name}: status/gates are derived state and must not be stored in manifest")
    if manifest.get("change_id") != state.get("change_id"):
        errors.append(f"{change_dir.name}: manifest/state change_id mismatch")
    if manifest.get("risk_level") != state.get("risk_level"):
        errors.append(f"{change_dir.name}: manifest/state risk_level mismatch")
    authors = set(manifest.get("authors") or [])
    if not authors or "REPLACE_ME" in authors:
        errors.append(f"{change_dir.name}: manifest requires named authors")

    evidence: dict[str, dict] = {}
    for path in sorted((change_dir / "evidence").glob("*.json")) if (change_dir / "evidence").exists() else []:
        record = load_json(path)
        validate_schema(record, "evidence.schema.json", path)
        eid = record.get("evidence_id")
        if not eid or eid in evidence:
            errors.append(f"{change_dir.name}: invalid or duplicate evidence id in {path.name}")
        evidence[eid] = record
        if record.get("change_id") != state.get("change_id"):
            errors.append(f"{change_dir.name}: evidence {eid} belongs to another change")
        uri = record.get("uri", "")
        artifact = ROOT / uri
        if artifact.is_file():
            actual = evidence_sha256(artifact)
            if actual.lower() != record.get("sha256", "").lower():
                errors.append(f"{change_dir.name}: evidence {eid} hash mismatch for {uri}")
        elif "://" not in uri or uri.split("://", 1)[0] not in POLICY["evidence"]["external_uri_schemes"]:
            errors.append(f"{change_dir.name}: evidence {eid} URI is missing or not allowed: {uri}")

    approvals: dict[str, list[dict]] = {}
    gate_actors: set[tuple[str, str]] = set()
    actor_roles: dict[str, set[str]] = {}
    high_risk = state.get("risk_level") in POLICY["high_risk"]["levels"]
    for path in sorted((change_dir / "approvals").glob("*.json")) if (change_dir / "approvals").exists() else []:
        record = load_json(path)
        validate_schema(record, "approval.schema.json", path)
        gate = record.get("gate", "")
        rule = POLICY["gate_policy"].get(gate)
        if not rule:
            errors.append(f"{change_dir.name}: unknown gate in {path.name}")
            continue
        if record.get("change_id") != state.get("change_id"):
            errors.append(f"{change_dir.name}: approval {record.get('approval_id')} belongs to another change")
        if record.get("decision") != "approved":
            continue
        actor = record.get("actor_id", "")
        role = record.get("actor_role", "")
        if role not in rule["roles"]:
            errors.append(f"{change_dir.name}: {role} cannot approve {gate}")
        missing = set(record.get("evidence_ids", [])) - evidence.keys()
        if missing:
            errors.append(f"{change_dir.name}: approval {record.get('approval_id')} references missing evidence {sorted(missing)}")
        identity = (gate, actor)
        if identity in gate_actors:
            errors.append(f"{change_dir.name}: duplicate approver {actor} for {gate}")
        gate_actors.add(identity)
        provider = record.get("identity_provider")
        is_example = state.get("change_id", "").startswith("CHG-EXAMPLE-")
        example_allowed = POLICY["trusted_identity"].get("allow_example_identity_for_example_changes") and is_example
        if provider not in POLICY["trusted_identity"]["providers"] and not (example_allowed and provider == "example-oidc"):
            errors.append(f"{change_dir.name}: untrusted identity provider {provider}")
        if POLICY["trusted_identity"]["require_commit_sha"] and not record.get("commit_sha") and not example_allowed:
            errors.append(f"{change_dir.name}: approval {record.get('approval_id')} must bind a commit SHA")
        if high_risk:
            if POLICY["high_risk"]["author_cannot_approve"] and actor in authors:
                errors.append(f"{change_dir.name}: author {actor} cannot approve high-risk change")
            if POLICY["high_risk"]["producer_cannot_approve_own_evidence"]:
                owned = [eid for eid in record.get("evidence_ids", []) if evidence.get(eid, {}).get("producer") == actor]
                if owned:
                    errors.append(f"{change_dir.name}: {actor} cannot approve own evidence {owned}")
            actor_roles.setdefault(actor, set()).add(role)
        approvals.setdefault(gate, []).append(record)

    if high_risk and POLICY["high_risk"]["separation_of_duties"]:
        for actor, roles in actor_roles.items():
            for exclusive in POLICY["high_risk"]["mutually_exclusive_roles"]:
                conflict = roles.intersection(exclusive)
                if len(conflict) > 1:
                    errors.append(f"{change_dir.name}: {actor} holds mutually exclusive approval roles {sorted(conflict)}")

    gates = derived_gates(approvals)
    needed_gate = POLICY["required_gate_for_target"].get(state.get("status"))
    if needed_gate and gates.get(needed_gate) != "approved":
        errors.append(f"{change_dir.name}: status {state.get('status')} requires approved {needed_gate}")

for warning in warnings:
    print("WARNING:", warning)
for error in errors:
    print("ERROR:", error)
print(f"Enterprise validation: {len(errors)} error(s), {len(warnings)} warning(s)")
sys.exit(1 if errors or (POLICY.get("fail_on_warnings") and warnings) else 0)
