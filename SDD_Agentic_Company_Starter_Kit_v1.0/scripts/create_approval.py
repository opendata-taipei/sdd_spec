#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / "config" / "enterprise-policy.json").read_text(encoding="utf-8"))
parser = argparse.ArgumentParser(description="Create a gate approval from trusted CI/OIDC identity context")
parser.add_argument("--change", required=True)
parser.add_argument("--gate", required=True, choices=POLICY["gate_policy"].keys())
parser.add_argument("--evidence", required=True, nargs="+")
args = parser.parse_args()

identity = {
    "actor_id": os.environ.get("SDD_ACTOR_ID"),
    "actor_role": os.environ.get("SDD_ACTOR_ROLE"),
    "identity_provider": os.environ.get("SDD_IDENTITY_PROVIDER"),
    "identity_claim": os.environ.get("SDD_IDENTITY_CLAIM"),
    "commit_sha": os.environ.get("SDD_COMMIT_SHA"),
}
missing = [key for key, value in identity.items() if not value]
if missing:
    raise SystemExit(f"Trusted identity context missing: {', '.join(missing)}")
if identity["identity_provider"] not in POLICY["trusted_identity"]["providers"]:
    raise SystemExit("Identity provider is not trusted by enterprise policy")
if identity["actor_role"] not in POLICY["gate_policy"][args.gate]["roles"]:
    raise SystemExit(f"Role {identity['actor_role']} cannot approve {args.gate}")
if not re.fullmatch(r"[a-fA-F0-9]{40}", identity["commit_sha"] or ""):
    raise SystemExit("SDD_COMMIT_SHA must be a full 40-character Git SHA")

matches = [p for p in (ROOT / "changes").glob(args.change + "*") if p.is_dir()]
if len(matches) != 1:
    raise SystemExit(f"Expected one change directory, found {len(matches)}")
change_dir = matches[0]
state = json.loads((change_dir / "state.json").read_text(encoding="utf-8"))
known_evidence = {json.loads(p.read_text(encoding="utf-8"))["evidence_id"] for p in (change_dir / "evidence").glob("*.json")}
unknown = set(args.evidence) - known_evidence
if unknown:
    raise SystemExit(f"Unknown evidence: {sorted(unknown)}")

approval_id = f"APR-{args.gate.split('_', 1)[0]}-{identity['actor_id'].upper()}"
record = {
    "approval_id": approval_id,
    "change_id": state["change_id"],
    "gate": args.gate,
    "decision": "approved",
    **identity,
    "decided_at": datetime.now(timezone.utc).isoformat(),
    "evidence_ids": args.evidence,
}
target = change_dir / "approvals" / f"{approval_id}.json"
target.parent.mkdir(exist_ok=True)
if target.exists():
    raise SystemExit(f"Approval already exists: {target.relative_to(ROOT)}")
target.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(target.relative_to(ROOT))
