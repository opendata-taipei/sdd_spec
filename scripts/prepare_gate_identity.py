#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from gate_identity import (
    GateIdentityError,
    OIDC_RESPONSE_MAX_BYTES,
    actor_pseudonym,
    load_protected_role_map,
    parse_oidc_response,
    reduced_identity_claim,
    resolve_gate_role,
    validate_oidc_claims,
)

ROOT = Path(__file__).resolve().parents[1]


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if value is None or value == "":
        raise GateIdentityError(f"required trusted context is missing: {name}")
    return value


def _write_outputs(path: Path, values: dict[str, str]) -> None:
    for key, value in values.items():
        if "\n" in value or "\r" in value:
            raise GateIdentityError("workflow output contains a line break")
    payload = "".join(f"{key}={value}\n" for key, value in values.items())
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(payload)


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare privacy-preserving GitHub OIDC Gate identity")
    parser.add_argument("--oidc-response", required=True, type=Path)
    parser.add_argument("--gate", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        output = args.output or Path(_required_env("GITHUB_OUTPUT"))
        policy = json.loads((ROOT / "config/enterprise-policy.json").read_text(encoding="utf-8"))
        role_map = load_protected_role_map(
            _required_env("SDD_GITHUB_ROLE_MAP_JSON"), set(policy["allowed_roles"])
        )
        repository_id = _required_env("GITHUB_REPOSITORY_ID")
        actor_id = _required_env("GITHUB_ACTOR_ID")
        workflow_ref = _required_env("GITHUB_WORKFLOW_REF")
        run_id = _required_env("GITHUB_RUN_ID")
        commit_sha = _required_env("GITHUB_SHA")
        with args.oidc_response.open("r", encoding="utf-8") as handle:
            raw_response = handle.read(OIDC_RESPONSE_MAX_BYTES + 1)
        _, claims = parse_oidc_response(raw_response)
        validate_oidc_claims(
            claims,
            repository_id=repository_id,
            actor_id=actor_id,
            workflow_ref=workflow_ref,
            run_id=run_id,
            commit_sha=commit_sha,
        )
        actor_ref = actor_pseudonym(
            repository_id, actor_id, _required_env("SDD_IDENTITY_PEPPER_B64")
        )
        role = resolve_gate_role(role_map, actor_id, args.gate, policy)
        identity_claim = reduced_identity_claim(
            claims,
            actor_ref,
            repository_id=repository_id,
            workflow_ref=workflow_ref,
            run_id=run_id,
        )
        _write_outputs(output, {
            "actor_id": actor_ref,
            "actor_role": role,
            "identity_claim": identity_claim,
            "commit_sha": commit_sha.lower(),
        })
    except (GateIdentityError, OSError, UnicodeError, KeyError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Gate identity preparation failed: {exc}") from None
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
