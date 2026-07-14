#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from gate_identity import GateIdentityError, load_protected_role_map, resolve_gate_role

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve one Gate role from protected runtime mapping")
    parser.add_argument("--actor-id", required=True)
    parser.add_argument("--gate", required=True)
    args = parser.parse_args()
    try:
        policy = json.loads((ROOT / "config/enterprise-policy.json").read_text(encoding="utf-8"))
        raw_mapping = os.environ.get("SDD_GITHUB_ROLE_MAP_JSON")
        if raw_mapping is None:
            raise GateIdentityError("protected role map is required")
        mapping = load_protected_role_map(raw_mapping, set(policy["allowed_roles"]))
        role = resolve_gate_role(mapping, args.actor_id, args.gate, policy)
    except (GateIdentityError, KeyError, OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Role resolution failed: {exc}") from None
    print(role)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
