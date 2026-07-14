#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from gate_identity import (
    GateIdentityError,
    approval_id as build_approval_id,
    validate_reduced_identity_claim,
)

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / "config" / "enterprise-policy.json").read_text(encoding="utf-8"))
CHANGE_PATTERN = re.compile(r"CHG-[0-9]{4}-[0-9]{3,}")
EVIDENCE_PATTERN = re.compile(r"EVD-[A-Z0-9-]+")


def _inputs(args: argparse.Namespace) -> tuple[str, str, list[str]]:
    if args.from_env:
        change = os.environ.get("SDD_CHANGE_INPUT", "")
        gate = os.environ.get("SDD_GATE_INPUT", "")
        evidence = os.environ.get("SDD_EVIDENCE_IDS_INPUT", "").split()
    else:
        change = args.change or ""
        gate = args.gate or ""
        evidence = args.evidence or []
    if not CHANGE_PATTERN.fullmatch(change):
        raise GateIdentityError("Change ID does not match the required contract")
    if gate not in POLICY["gate_policy"]:
        raise GateIdentityError("Gate is not defined by enterprise policy")
    if not evidence or len(evidence) > 100 or len(evidence) != len(set(evidence)):
        raise GateIdentityError("Evidence list is missing, duplicated, or too large")
    if any(not EVIDENCE_PATTERN.fullmatch(item) for item in evidence):
        raise GateIdentityError("Evidence ID does not match the required contract")
    return change, gate, evidence


def _identity(gate: str) -> dict[str, str]:
    identity = {
        "actor_id": os.environ.get("SDD_ACTOR_ID", ""),
        "actor_role": os.environ.get("SDD_ACTOR_ROLE", ""),
        "identity_provider": os.environ.get("SDD_IDENTITY_PROVIDER", ""),
        "identity_claim": os.environ.get("SDD_IDENTITY_CLAIM", ""),
        "commit_sha": os.environ.get("SDD_COMMIT_SHA", ""),
    }
    missing = [key for key, value in identity.items() if not value]
    if missing:
        raise GateIdentityError(f"Trusted identity context is incomplete: {', '.join(missing)}")
    if identity["identity_provider"] not in POLICY["trusted_identity"]["providers"]:
        raise GateIdentityError("Identity provider is not trusted by enterprise policy")
    if identity["actor_role"] not in POLICY["gate_policy"][gate]["roles"]:
        raise GateIdentityError("Actor role cannot approve the requested Gate")
    if not re.fullmatch(r"[a-fA-F0-9]{40}", identity["commit_sha"]):
        raise GateIdentityError("Commit SHA must contain 40 hexadecimal characters")
    identity["commit_sha"] = identity["commit_sha"].lower()
    if identity["identity_provider"] == "github-oidc":
        validate_reduced_identity_claim(identity["identity_claim"], identity["actor_id"])
    return identity


def _write_atomic_no_replace(target: Path, record: dict) -> None:
    target.parent.mkdir(exist_ok=True)
    temporary = target.parent / f".{target.name}.{uuid.uuid4().hex}.tmp"
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(record, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, target)
        except FileExistsError as exc:
            raise GateIdentityError("Approval target already exists") from exc
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Gate Approval from trusted CI/OIDC context")
    parser.add_argument("--from-env", action="store_true")
    parser.add_argument("--change")
    parser.add_argument("--gate")
    parser.add_argument("--evidence", nargs="+")
    args = parser.parse_args()
    try:
        if args.from_env and any((args.change, args.gate, args.evidence)):
            raise GateIdentityError("--from-env cannot be combined with direct inputs")
        change, gate, evidence_ids = _inputs(args)
        identity = _identity(gate)
        matches = [path for path in (ROOT / "changes").glob(change + "-*") if path.is_dir()]
        if len(matches) != 1:
            raise GateIdentityError("Change ID must resolve to exactly one directory")
        change_dir = matches[0]
        state = json.loads((change_dir / "state.json").read_text(encoding="utf-8"))
        known_evidence = {
            json.loads(path.read_text(encoding="utf-8"))["evidence_id"]
            for path in (change_dir / "evidence").glob("*.json")
        }
        if set(evidence_ids) - known_evidence:
            raise GateIdentityError("Approval references unknown Evidence")
        approval_id = build_approval_id(
            identity["identity_provider"], identity["actor_id"], gate
        )
        record = {
            "approval_id": approval_id,
            "change_id": state["change_id"],
            "gate": gate,
            "decision": "approved",
            **identity,
            "decided_at": datetime.now(timezone.utc).isoformat(),
            "evidence_ids": evidence_ids,
        }
        target = change_dir / "approvals" / f"{approval_id}.json"
        _write_atomic_no_replace(target, record)
    except (GateIdentityError, OSError, KeyError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Approval creation failed: {exc}") from None
    print(target.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
