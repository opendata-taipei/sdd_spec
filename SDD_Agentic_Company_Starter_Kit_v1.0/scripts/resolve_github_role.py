#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--actor", required=True)
parser.add_argument("--gate", required=True)
args = parser.parse_args()
policy = json.loads((ROOT / "config/enterprise-policy.json").read_text(encoding="utf-8"))
mapping = json.loads((ROOT / "config/github-role-map.json").read_text(encoding="utf-8"))
roles = set(mapping.get("actors", {}).get(args.actor, []))
allowed = set(policy["gate_policy"].get(args.gate, {}).get("roles", []))
eligible = sorted(roles & allowed)
if len(eligible) != 1:
    raise SystemExit(f"Actor {args.actor} must map to exactly one eligible role for {args.gate}; found {eligible}")
print(eligible[0])
