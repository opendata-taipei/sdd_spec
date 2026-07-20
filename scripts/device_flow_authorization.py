#!/usr/bin/env python3
"""Provider-neutral primitives for TASK-010 synthetic device authorization.

This module performs no network calls and never receives a GitHub login, email,
device code, user token, App private key, or installation token. A private managed
adapter is responsible for device-flow transport and passes only the fresh numeric
``GET /user`` result into these fail-closed primitives.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import stat
from pathlib import Path
from typing import Any

from gate_identity import (
    ACTOR_REF_PATTERN,
    GateIdentityError,
    actor_pseudonym,
    load_protected_role_map,
    validate_numeric_id,
)
from merge_authorization import (
    CHECK_NAME,
    CHECK_VERSION,
    MergeAuthorizationError,
    _decode_key,
    _validate_request,
    canonical_digest,
    canonical_json,
)

ATTESTATION_V2 = "merge-authz-attestation/v2"
TRIGGER_MODE = "poll-device-flow"
MAX_AUTHORIZATION_TTL_SECONDS = 600
V2_KEYS = {
    "schema_version", "request_digest", "decision",
    "authorization_policy_result", "trigger_mode",
    "controller_artifact_digest", "configuration_digest", "app_id_digest",
    "installation_scope_digest", "identity_decision_digest",
    "device_session_digest", "issued_at", "expires_at", "signature",
}


class DeviceAuthorizationError(MergeAuthorizationError):
    """Safe failure that exposes only a stable non-sensitive code."""


def _digest(value: Any, code: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise DeviceAuthorizationError(code)
    if any(character not in "0123456789abcdef" for character in value):
        raise DeviceAuthorizationError(code)
    return value


def _positive_int(value: Any, code: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise DeviceAuthorizationError(code)
    return value


def _private_policy(policy: Any) -> tuple[set[str], set[str]]:
    if not isinstance(policy, dict):
        raise DeviceAuthorizationError("private_policy_invalid")
    expected = {
        "role_namespace", "eligible_authorizer_roles",
        "incompatible_authorizer_roles", "identity_key", "mapping_location",
        "fresh_device_flow_per_decision", "refresh_token_storage",
    }
    if set(policy) != expected:
        raise DeviceAuthorizationError("private_policy_invalid")
    if (
        policy.get("role_namespace") != "merge-authorization/v1"
        or policy.get("identity_key") != "github_numeric_user_id"
        or policy.get("mapping_location") != "private-overlay-only"
        or policy.get("fresh_device_flow_per_decision") is not True
        or policy.get("refresh_token_storage") is not False
    ):
        raise DeviceAuthorizationError("private_policy_invalid")
    eligible = policy.get("eligible_authorizer_roles")
    incompatible = policy.get("incompatible_authorizer_roles")
    if (
        not isinstance(eligible, list) or eligible != ["change_manager"]
        or not isinstance(incompatible, list) or not incompatible
        or any(not isinstance(role, str) or not role for role in incompatible)
        or len(incompatible) != len(set(incompatible))
        or "change_manager" in incompatible
    ):
        raise DeviceAuthorizationError("private_policy_invalid")
    return set(eligible), set(incompatible)


def authorize_device_identity(
    request: dict[str, Any], *, authenticated_user_id: str,
    pull_request_author_id: str, approval_actor_ref: str,
    private_role_map_json: str, private_policy: dict[str, Any],
    identity_pepper_b64: str, device_session_digest: str,
) -> str:
    """Return only an opaque decision digest after fresh private authorization."""
    _validate_request(request)
    if request["classification"] != "approval":
        raise DeviceAuthorizationError("device_authorization_not_applicable")
    _digest(device_session_digest, "device_session_digest_invalid")
    try:
        authenticated_user_id = validate_numeric_id(
            authenticated_user_id, label="authenticated user ID"
        )
        pull_request_author_id = validate_numeric_id(
            pull_request_author_id, label="pull request author ID"
        )
    except GateIdentityError as exc:
        raise DeviceAuthorizationError("device_identity_invalid") from exc
    if authenticated_user_id == pull_request_author_id:
        raise DeviceAuthorizationError("device_author_is_pr_author")
    eligible, incompatible = _private_policy(private_policy)
    try:
        mapping = load_protected_role_map(
            private_role_map_json, eligible.union(incompatible)
        )
    except GateIdentityError as exc:
        raise DeviceAuthorizationError("private_role_map_invalid") from exc
    roles = set(mapping.get(authenticated_user_id, ()))
    if len(roles.intersection(eligible)) != 1:
        raise DeviceAuthorizationError("device_role_not_unique")
    if roles.intersection(incompatible):
        raise DeviceAuthorizationError("device_role_separation_failed")
    try:
        reviewer_ref = actor_pseudonym(
            request["repository_id"], authenticated_user_id, identity_pepper_b64
        )
    except GateIdentityError as exc:
        raise DeviceAuthorizationError("device_identity_pseudonym_invalid") from exc
    if not isinstance(approval_actor_ref, str) or not ACTOR_REF_PATTERN.fullmatch(approval_actor_ref):
        raise DeviceAuthorizationError("approval_actor_ref_invalid")
    if hmac.compare_digest(reviewer_ref, approval_actor_ref):
        raise DeviceAuthorizationError("device_author_is_approval_actor")
    private_decision = {
        "schema_version": "merge-authz-identity-decision/v1",
        "request_digest": canonical_digest(request),
        "reviewer_ref": reviewer_ref,
        "eligible_role": "change_manager",
        "device_session_digest": device_session_digest,
        "result": "passed",
    }
    return canonical_digest(private_decision)


class FreshDeviceSessionStore:
    """Atomic private store that rejects every reused device authorization session."""

    def __init__(self, root: Path):
        if not isinstance(root, Path) or (root.exists() and root.is_symlink()):
            raise DeviceAuthorizationError("device_store_path_invalid")
        root.mkdir(parents=True, exist_ok=True)
        if root.is_symlink() or not root.is_dir():
            raise DeviceAuthorizationError("device_store_path_invalid")
        self.root = root

    def claim(self, device_session_digest: str, request_digest: str, *, now: int) -> None:
        session = _digest(device_session_digest, "device_session_digest_invalid")
        request = _digest(request_digest, "device_request_digest_invalid")
        _positive_int(now, "device_session_time_invalid")
        target = self.root / f"{session}.json"
        if target.parent != self.root or target.is_symlink():
            raise DeviceAuthorizationError("device_store_path_invalid")
        record = {
            "schema_version": "merge-authz-device-session/v1",
            "device_session_digest": session,
            "request_digest": request,
            "recorded_at": now,
        }
        try:
            descriptor = os.open(
                target, os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                stat.S_IRUSR | stat.S_IWUSR,
            )
        except FileExistsError as exc:
            raise DeviceAuthorizationError("device_session_reused") from exc
        except OSError as exc:
            raise DeviceAuthorizationError("device_store_write_failed") from exc
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(canonical_json(record) + b"\n")
                handle.flush()
                os.fsync(handle.fileno())
        except OSError as exc:
            try:
                target.unlink(missing_ok=True)
            except OSError:
                pass
            raise DeviceAuthorizationError("device_store_write_failed") from exc


def validate_poll_freshness(
    request: dict[str, Any], *, current_head_sha: str, current_base_sha: str,
    current_policy: dict[str, Any], current_installation_scope_digest: str,
    expected_installation_scope_digest: str, now: int,
) -> None:
    _validate_request(request)
    _positive_int(now, "poll_time_invalid")
    current_scope = _digest(
        current_installation_scope_digest, "installation_scope_digest_invalid"
    )
    expected_scope = _digest(
        expected_installation_scope_digest, "installation_scope_digest_invalid"
    )
    if (
        request["head_sha"] != current_head_sha
        or request["base_sha"] != current_base_sha
        or request["policy_sha256"] != canonical_digest(current_policy)
        or not hmac.compare_digest(current_scope, expected_scope)
    ):
        raise DeviceAuthorizationError("poll_context_stale")
    if now < request["issued_at"] or now > request["expires_at"]:
        raise DeviceAuthorizationError("poll_request_expired")


def _v2_payload(attestation: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in attestation.items() if key != "signature"}


def _validate_v2(attestation: Any) -> dict[str, Any]:
    if not isinstance(attestation, dict) or set(attestation) != V2_KEYS:
        raise DeviceAuthorizationError("attestation_v2_contract_invalid")
    if (
        attestation.get("schema_version") != ATTESTATION_V2
        or attestation.get("trigger_mode") != TRIGGER_MODE
        or attestation.get("decision") not in {"approved", "denied"}
        or attestation.get("authorization_policy_result") not in {"passed", "failed"}
    ):
        raise DeviceAuthorizationError("attestation_v2_contract_invalid")
    for key in (
        "request_digest", "controller_artifact_digest", "configuration_digest",
        "app_id_digest", "installation_scope_digest", "identity_decision_digest",
        "device_session_digest",
    ):
        _digest(attestation.get(key), f"{key}_invalid")
    issued = _positive_int(attestation.get("issued_at"), "attestation_v2_time_invalid")
    expires = _positive_int(attestation.get("expires_at"), "attestation_v2_time_invalid")
    if expires <= issued or expires - issued > MAX_AUTHORIZATION_TTL_SECONDS:
        raise DeviceAuthorizationError("attestation_v2_window_invalid")
    signature = attestation.get("signature")
    if (
        not isinstance(signature, str) or not signature.startswith("hmac-sha256:")
        or len(signature) != len("hmac-sha256:") + 64
    ):
        raise DeviceAuthorizationError("attestation_v2_signature_invalid")
    _digest(signature.split(":", 1)[1], "attestation_v2_signature_invalid")
    return attestation


def sign_device_attestation(
    request: dict[str, Any], *, identity_decision_digest: str,
    device_session_digest: str, controller_artifact_digest: str,
    configuration_digest: str, app_id_digest: str,
    installation_scope_digest: str, key_b64: str,
    issued_at: int, expires_at: int,
) -> dict[str, Any]:
    _validate_request(request)
    if request["classification"] != "approval":
        raise DeviceAuthorizationError("attestation_v2_not_applicable")
    key = _decode_key(key_b64)
    attestation = {
        "schema_version": ATTESTATION_V2,
        "request_digest": canonical_digest(request),
        "decision": "approved",
        "authorization_policy_result": "passed",
        "trigger_mode": TRIGGER_MODE,
        "controller_artifact_digest": controller_artifact_digest,
        "configuration_digest": configuration_digest,
        "app_id_digest": app_id_digest,
        "installation_scope_digest": installation_scope_digest,
        "identity_decision_digest": identity_decision_digest,
        "device_session_digest": device_session_digest,
        "issued_at": issued_at,
        "expires_at": expires_at,
        "signature": "hmac-sha256:" + "0" * 64,
    }
    _validate_v2(attestation)
    if issued_at < request["issued_at"] or expires_at > request["expires_at"]:
        raise DeviceAuthorizationError("attestation_v2_window_outside_request")
    signature = hmac.new(
        key,
        b"SDD_MERGE_AUTHZ_ATTESTATION_V2\0" + canonical_json(_v2_payload(attestation)),
        hashlib.sha256,
    ).hexdigest()
    attestation["signature"] = "hmac-sha256:" + signature
    return attestation


def verify_device_attestation(
    request: dict[str, Any], attestation: dict[str, Any], *, key_b64: str,
    current_head_sha: str, current_base_sha: str, current_policy: dict[str, Any],
    current_installation_scope_digest: str, controller_artifact_digest: str,
    configuration_digest: str, app_id_digest: str, now: int,
) -> str:
    _validate_request(request)
    _validate_v2(attestation)
    key = _decode_key(key_b64)
    validate_poll_freshness(
        request, current_head_sha=current_head_sha, current_base_sha=current_base_sha,
        current_policy=current_policy,
        current_installation_scope_digest=current_installation_scope_digest,
        expected_installation_scope_digest=attestation["installation_scope_digest"],
        now=now,
    )
    for key_name, expected in (
        ("controller_artifact_digest", controller_artifact_digest),
        ("configuration_digest", configuration_digest),
        ("app_id_digest", app_id_digest),
    ):
        _digest(expected, f"current_{key_name}_invalid")
        if not hmac.compare_digest(attestation[key_name], expected):
            raise DeviceAuthorizationError("controller_context_stale")
    if (
        attestation["request_digest"] != canonical_digest(request)
        or attestation["issued_at"] < request["issued_at"]
        or attestation["expires_at"] > request["expires_at"]
        or now > attestation["expires_at"]
    ):
        raise DeviceAuthorizationError("attestation_v2_stale")
    expected_signature = hmac.new(
        key,
        b"SDD_MERGE_AUTHZ_ATTESTATION_V2\0" + canonical_json(_v2_payload(attestation)),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(
        attestation["signature"].split(":", 1)[1], expected_signature
    ):
        raise DeviceAuthorizationError("attestation_v2_signature_mismatch")
    if (
        attestation["decision"] != "approved"
        or attestation["authorization_policy_result"] != "passed"
    ):
        raise DeviceAuthorizationError("device_authorization_denied")
    return canonical_digest(attestation)


def build_device_public_check_output(
    request: dict[str, Any], attestation: dict[str, Any], **verification: Any,
) -> dict[str, Any]:
    digest = verify_device_attestation(request, attestation, **verification)
    return {
        "schema_version": CHECK_VERSION,
        "check_name": CHECK_NAME,
        "conclusion": "success",
        "classification": request["classification"],
        "repository_id": request["repository_id"],
        "pull_request": request["pull_request"],
        "head_sha": request["head_sha"],
        "change_id": request["change_id"],
        "approval_sha256": request["approval_sha256"],
        "attestation_digest": digest,
    }
