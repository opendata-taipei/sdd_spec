#!/usr/bin/env python3
"""Fail-closed identity primitives for protected SDD gate workflows."""
from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import re
import struct
import time
from typing import Any

ROLE_MAP_MAX_BYTES = 32 * 1024
ROLE_MAP_MAX_ACTORS = 1000
OIDC_RESPONSE_MAX_BYTES = 64 * 1024
OIDC_TOKEN_MAX_BYTES = 32 * 1024
CLOCK_SKEW_SECONDS = 60
NUMERIC_ID_PATTERN = re.compile(r"[1-9][0-9]{0,19}")
ACTOR_REF_PATTERN = re.compile(r"ghoidc-v1:[a-f0-9]{64}")
ISSUER = "https://token.actions.githubusercontent.com"
AUDIENCE = "sdd-approval"
IDENTITY_VERSION = "github-oidc-reduced-v1"
REDUCED_CLAIM_KEYS = {
    "identity_version", "iss", "aud", "actor_ref", "repository_id",
    "workflow_ref", "run_id", "exp",
}


class GateIdentityError(ValueError):
    """Raised for untrusted or malformed gate identity input."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise GateIdentityError("JSON contains duplicate object keys")
        result[key] = value
    return result


def strict_json_loads(raw: str, *, max_bytes: int, label: str) -> Any:
    if not isinstance(raw, str):
        raise GateIdentityError(f"{label} must be text")
    try:
        size = len(raw.encode("utf-8"))
    except UnicodeEncodeError as exc:
        raise GateIdentityError(f"{label} is not valid UTF-8 text") from exc
    if size == 0 or size > max_bytes:
        raise GateIdentityError(f"{label} size is outside the allowed range")
    try:
        return json.loads(raw, object_pairs_hook=_reject_duplicate_keys)
    except GateIdentityError:
        raise
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise GateIdentityError(f"{label} is not valid JSON") from exc


def validate_numeric_id(value: str, *, label: str) -> str:
    if not isinstance(value, str) or not NUMERIC_ID_PATTERN.fullmatch(value):
        raise GateIdentityError(f"{label} must be a canonical numeric identifier")
    return value


def load_protected_role_map(raw: str, allowed_roles: set[str]) -> dict[str, tuple[str, ...]]:
    document = strict_json_loads(raw, max_bytes=ROLE_MAP_MAX_BYTES, label="protected role map")
    if not isinstance(document, dict) or set(document) != {"schema_version", "actors"}:
        raise GateIdentityError("protected role map does not match the required contract")
    if document["schema_version"] != "1.0" or not isinstance(document["actors"], dict):
        raise GateIdentityError("protected role map does not match the required contract")
    actors = document["actors"]
    if len(actors) > ROLE_MAP_MAX_ACTORS:
        raise GateIdentityError("protected role map exceeds the actor limit")
    result: dict[str, tuple[str, ...]] = {}
    for actor_id, roles in actors.items():
        validate_numeric_id(actor_id, label="actor ID")
        if not isinstance(roles, list) or not roles:
            raise GateIdentityError("each actor must have a non-empty role array")
        if any(not isinstance(role, str) for role in roles):
            raise GateIdentityError("roles must be strings")
        if len(roles) != len(set(roles)):
            raise GateIdentityError("role arrays must not contain duplicates")
        if not set(roles).issubset(allowed_roles):
            raise GateIdentityError("protected role map contains an unknown role")
        result[actor_id] = tuple(roles)
    return result


def resolve_gate_role(
    mapping: dict[str, tuple[str, ...]], actor_id: str, gate: str, policy: dict[str, Any]
) -> str:
    validate_numeric_id(actor_id, label="actor ID")
    gate_policy = policy.get("gate_policy", {})
    if gate not in gate_policy:
        raise GateIdentityError("unknown gate")
    actor_roles = set(mapping.get(actor_id, ()))
    eligible = actor_roles.intersection(gate_policy[gate].get("roles", []))
    if len(eligible) != 1:
        raise GateIdentityError("actor must have exactly one eligible role for the gate")
    return next(iter(eligible))


def decode_pepper(value: str) -> bytes:
    if not isinstance(value, str) or not value:
        raise GateIdentityError("identity pepper is missing or invalid")
    try:
        decoded = base64.b64decode(value, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise GateIdentityError("identity pepper is missing or invalid") from exc
    if len(decoded) != 32 or base64.b64encode(decoded).decode("ascii") != value:
        raise GateIdentityError("identity pepper is missing or invalid")
    return decoded


def actor_pseudonym(repository_id: str, actor_id: str, pepper_b64: str) -> str:
    repository_id = validate_numeric_id(repository_id, label="repository ID")
    actor_id = validate_numeric_id(actor_id, label="actor ID")
    pepper = decode_pepper(pepper_b64)
    repository = repository_id.encode("ascii")
    actor = actor_id.encode("ascii")
    message = (
        b"SDD_GATE_ACTOR_V1\0"
        + struct.pack(">I", len(repository)) + repository
        + struct.pack(">I", len(actor)) + actor
    )
    return "ghoidc-v1:" + hmac.new(pepper, message, hashlib.sha256).hexdigest()


def _decode_base64url(segment: str, *, label: str) -> bytes:
    if not isinstance(segment, str) or not segment or not re.fullmatch(r"[A-Za-z0-9_-]+", segment):
        raise GateIdentityError(f"OIDC {label} is malformed")
    try:
        decoded = base64.urlsafe_b64decode(segment + "=" * (-len(segment) % 4))
    except (binascii.Error, ValueError) as exc:
        raise GateIdentityError(f"OIDC {label} is malformed") from exc
    canonical = base64.urlsafe_b64encode(decoded).decode("ascii").rstrip("=")
    if canonical != segment:
        raise GateIdentityError(f"OIDC {label} is not canonical")
    return decoded


def parse_oidc_response(raw: str) -> tuple[dict[str, Any], dict[str, Any]]:
    response = strict_json_loads(raw, max_bytes=OIDC_RESPONSE_MAX_BYTES, label="OIDC response")
    if not isinstance(response, dict) or set(response) != {"value"} or not isinstance(response["value"], str):
        raise GateIdentityError("OIDC response does not match the required contract")
    token = response["value"]
    if len(token.encode("utf-8")) > OIDC_TOKEN_MAX_BYTES:
        raise GateIdentityError("OIDC token exceeds the size limit")
    parts = token.split(".")
    if len(parts) != 3 or not all(parts):
        raise GateIdentityError("OIDC token must contain three segments")
    try:
        header = strict_json_loads(
            _decode_base64url(parts[0], label="header").decode("utf-8"),
            max_bytes=4096,
            label="OIDC header",
        )
        claims = strict_json_loads(
            _decode_base64url(parts[1], label="payload").decode("utf-8"),
            max_bytes=OIDC_TOKEN_MAX_BYTES,
            label="OIDC payload",
        )
    except UnicodeDecodeError as exc:
        raise GateIdentityError("OIDC token JSON is not UTF-8") from exc
    _decode_base64url(parts[2], label="signature")
    if not isinstance(header, dict) or not isinstance(claims, dict):
        raise GateIdentityError("OIDC token header and payload must be objects")
    if header.get("alg") != "RS256":
        raise GateIdentityError("OIDC token algorithm is not allowed")
    return header, claims


def validate_oidc_claims(
    claims: dict[str, Any], *, repository_id: str, actor_id: str,
    workflow_ref: str, run_id: str, commit_sha: str, now: int | None = None,
) -> dict[str, Any]:
    repository_id = validate_numeric_id(repository_id, label="expected repository ID")
    actor_id = validate_numeric_id(actor_id, label="expected actor ID")
    run_id = validate_numeric_id(run_id, label="expected run ID")
    if not isinstance(workflow_ref, str) or not workflow_ref or "\n" in workflow_ref or "\r" in workflow_ref:
        raise GateIdentityError("expected workflow reference is invalid")
    if not isinstance(commit_sha, str) or not re.fullmatch(r"[a-fA-F0-9]{40}", commit_sha):
        raise GateIdentityError("expected commit SHA is invalid")
    expected = {
        "iss": ISSUER,
        "aud": AUDIENCE,
        "repository_id": repository_id,
        "actor_id": actor_id,
        "workflow_ref": workflow_ref,
        "run_id": run_id,
    }
    for key, value in expected.items():
        if claims.get(key) != value:
            raise GateIdentityError("OIDC claims do not match the trusted workflow context")
    temporal: dict[str, int] = {}
    for key in ("iat", "nbf", "exp"):
        value = claims.get(key)
        if isinstance(value, bool) or not isinstance(value, int):
            raise GateIdentityError("OIDC temporal claims are invalid")
        temporal[key] = value
    current = int(time.time()) if now is None else now
    if temporal["iat"] > current + CLOCK_SKEW_SECONDS:
        raise GateIdentityError("OIDC token was issued in the future")
    if temporal["nbf"] > current + CLOCK_SKEW_SECONDS:
        raise GateIdentityError("OIDC token is not active")
    if temporal["exp"] < current - CLOCK_SKEW_SECONDS or temporal["exp"] <= temporal["iat"]:
        raise GateIdentityError("OIDC token is expired or has an invalid lifetime")
    return temporal


def reduced_identity_claim(
    claims: dict[str, Any], actor_ref: str, *, repository_id: str,
    workflow_ref: str, run_id: str,
) -> str:
    if not ACTOR_REF_PATTERN.fullmatch(actor_ref):
        raise GateIdentityError("actor reference is invalid")
    reduced = {
        "identity_version": IDENTITY_VERSION,
        "iss": claims["iss"],
        "aud": claims["aud"],
        "actor_ref": actor_ref,
        "repository_id": repository_id,
        "workflow_ref": workflow_ref,
        "run_id": run_id,
        "exp": claims["exp"],
    }
    return json.dumps(reduced, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def validate_reduced_identity_claim(raw: str, actor_ref: str) -> dict[str, Any]:
    if not ACTOR_REF_PATTERN.fullmatch(actor_ref or ""):
        raise GateIdentityError("github-oidc actor reference is invalid")
    claim = strict_json_loads(raw, max_bytes=4096, label="reduced identity claim")
    if not isinstance(claim, dict) or set(claim) != REDUCED_CLAIM_KEYS:
        raise GateIdentityError("reduced identity claim does not match the required contract")
    if claim.get("identity_version") != IDENTITY_VERSION or claim.get("iss") != ISSUER or claim.get("aud") != AUDIENCE:
        raise GateIdentityError("reduced identity claim has an invalid trust context")
    if claim.get("actor_ref") != actor_ref:
        raise GateIdentityError("reduced identity claim does not match the actor reference")
    validate_numeric_id(claim.get("repository_id"), label="claim repository ID")
    validate_numeric_id(claim.get("run_id"), label="claim run ID")
    if not isinstance(claim.get("workflow_ref"), str) or not claim["workflow_ref"]:
        raise GateIdentityError("reduced identity claim workflow reference is invalid")
    if isinstance(claim.get("exp"), bool) or not isinstance(claim.get("exp"), int):
        raise GateIdentityError("reduced identity claim expiry is invalid")
    return claim


def approval_id(identity_provider: str, actor_ref: str, gate: str) -> str:
    for value in (identity_provider, actor_ref, gate):
        if not isinstance(value, str) or not value or "\0" in value:
            raise GateIdentityError("approval identity input is invalid")
    message = b"SDD_APPROVAL_ID_V1\0" + b"\0".join(
        value.encode("utf-8") for value in (identity_provider, actor_ref, gate)
    )
    return f"APR-{gate.split('_', 1)[0]}-ID-V1-{hashlib.sha256(message).hexdigest().upper()}"
