#!/usr/bin/env python3
"""Fail-closed primitives for the Mode B private merge authorization sandbox.

The module is intentionally network- and provider-client-free. A private GitHub App
adapter must fetch the current PR state, call these primitives, and write the check
with an installation token. No function merges a pull request or resolves private
reviewer identity.
"""
from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import os
import re
import stat
from pathlib import Path, PurePosixPath
from typing import Any

REQUEST_VERSION = "merge-authz-request/v1"
ATTESTATION_VERSION = "merge-authz-attestation/v1"
CHECK_VERSION = "merge-authz-check/v1"
CHECK_NAME = "approval-merge-authorization"
MAX_APPROVAL_BYTES = 64 * 1024
MAX_WEBHOOK_BYTES = 1024 * 1024
MAX_DELIVERY_ID_BYTES = 128
MAX_AUTHORIZATION_TTL_SECONDS = 600
MAX_JSON_BYTES = 128 * 1024

SHA_PATTERN = re.compile(r"[a-f0-9]{40}")
DIGEST_PATTERN = re.compile(r"[a-f0-9]{64}")
NUMERIC_ID_PATTERN = re.compile(r"[1-9][0-9]{0,19}")
CHANGE_ID_PATTERN = re.compile(r"CHG-[0-9]{4}-[0-9]{3,}")
BASE_REF_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,254}")
APPROVAL_FILE_PATTERN = re.compile(
    r"changes/(?P<directory>CHG-[0-9]{4}-[0-9]{3,}-[A-Za-z0-9._-]+)/approvals/"
    r"(?P<approval>APR-[A-Z0-9-]+)[.]json"
)
APPROVAL_KEYS = {
    "approval_id", "change_id", "gate", "decision", "actor_id", "actor_role",
    "decided_at", "evidence_ids", "identity_provider", "identity_claim", "commit_sha",
}
FILE_KEYS = {"path", "status", "size", "sha256", "is_symlink", "is_submodule"}
REQUEST_KEYS = {
    "schema_version", "repository_id", "pull_request", "head_sha", "base_sha",
    "base_ref", "classification", "change_id", "approval_path", "approval_sha256",
    "target_commit", "policy_sha256", "nonce", "issued_at", "expires_at",
}
ATTESTATION_KEYS = {
    "schema_version", "request_digest", "decision", "review_policy_result",
    "control_workflow_ref", "issued_at", "expires_at", "signature",
}


class MergeAuthorizationError(ValueError):
    """Safe failure carrying only a stable, non-sensitive error code."""

    def __init__(self, code: str):
        if not isinstance(code, str) or not re.fullmatch(r"[a-z0-9_]{3,64}", code):
            code = "invalid_authorization_input"
        self.code = code
        super().__init__(code)


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise MergeAuthorizationError("duplicate_json_key")
        result[key] = value
    return result


def strict_json_loads(raw: bytes | str, *, max_bytes: int = MAX_JSON_BYTES) -> Any:
    if isinstance(raw, bytes):
        if not raw or len(raw) > max_bytes:
            raise MergeAuthorizationError("json_size_invalid")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise MergeAuthorizationError("json_utf8_invalid") from exc
    elif isinstance(raw, str):
        try:
            size = len(raw.encode("utf-8"))
        except UnicodeEncodeError as exc:
            raise MergeAuthorizationError("json_utf8_invalid") from exc
        if size == 0 or size > max_bytes:
            raise MergeAuthorizationError("json_size_invalid")
        text = raw
    else:
        raise MergeAuthorizationError("json_type_invalid")
    try:
        return json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    except MergeAuthorizationError:
        raise
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        raise MergeAuthorizationError("json_invalid") from exc


def canonical_json(document: Any) -> bytes:
    try:
        return json.dumps(
            document, ensure_ascii=True, sort_keys=True, separators=(",", ":"),
            allow_nan=False,
        ).encode("ascii")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise MergeAuthorizationError("canonical_json_invalid") from exc


def canonical_digest(document: Any) -> str:
    return hashlib.sha256(canonical_json(document)).hexdigest()


def _validate_sha(value: Any, *, code: str) -> str:
    if not isinstance(value, str) or not SHA_PATTERN.fullmatch(value):
        raise MergeAuthorizationError(code)
    return value


def _validate_digest(value: Any, *, code: str) -> str:
    if not isinstance(value, str) or not DIGEST_PATTERN.fullmatch(value):
        raise MergeAuthorizationError(code)
    return value


def _validate_positive_int(value: Any, *, code: str, maximum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise MergeAuthorizationError(code)
    if maximum is not None and value > maximum:
        raise MergeAuthorizationError(code)
    return value


def _validate_window(issued_at: Any, expires_at: Any) -> tuple[int, int]:
    issued = _validate_positive_int(issued_at, code="issued_at_invalid")
    expires = _validate_positive_int(expires_at, code="expires_at_invalid")
    if expires <= issued or expires - issued > MAX_AUTHORIZATION_TTL_SECONDS:
        raise MergeAuthorizationError("authorization_window_invalid")
    return issued, expires


def _validate_path(path: Any) -> str:
    if not isinstance(path, str) or not path or len(path.encode("utf-8")) > 1024:
        raise MergeAuthorizationError("diff_path_invalid")
    if "\\" in path or path.startswith("/") or "//" in path:
        raise MergeAuthorizationError("diff_path_invalid")
    parts = PurePosixPath(path).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise MergeAuthorizationError("diff_path_invalid")
    if PurePosixPath(path).as_posix() != path:
        raise MergeAuthorizationError("diff_path_invalid")
    return path


def _validate_diff_file(item: Any) -> dict[str, Any]:
    if not isinstance(item, dict) or set(item) != FILE_KEYS:
        raise MergeAuthorizationError("diff_file_contract_invalid")
    path = _validate_path(item["path"])
    if item["status"] not in {"added", "modified", "removed", "renamed"}:
        raise MergeAuthorizationError("diff_status_invalid")
    size = item["size"]
    if isinstance(size, bool) or not isinstance(size, int) or size < 0:
        raise MergeAuthorizationError("diff_size_invalid")
    _validate_digest(item["sha256"], code="diff_digest_invalid")
    if not isinstance(item["is_symlink"], bool) or not isinstance(item["is_submodule"], bool):
        raise MergeAuthorizationError("diff_type_invalid")
    return {**item, "path": path}


def _approval_candidate(path: str) -> bool:
    return "approvals" in PurePosixPath(path).parts


def _validate_approval_document(
    raw: bytes, path_match: re.Match[str], *, policy: dict[str, Any],
    known_evidence_ids: set[str],
) -> dict[str, Any]:
    if len(raw) > MAX_APPROVAL_BYTES:
        raise MergeAuthorizationError("approval_size_invalid")
    document = strict_json_loads(raw, max_bytes=MAX_APPROVAL_BYTES)
    if not isinstance(document, dict) or set(document) != APPROVAL_KEYS:
        raise MergeAuthorizationError("approval_contract_invalid")
    change_id = document.get("change_id")
    directory_change = path_match.group("directory").split("-", 3)
    directory_change_id = "-".join(directory_change[:3])
    if not isinstance(change_id, str) or not CHANGE_ID_PATTERN.fullmatch(change_id):
        raise MergeAuthorizationError("approval_change_invalid")
    if change_id != directory_change_id:
        raise MergeAuthorizationError("approval_change_mismatch")
    if document.get("approval_id") != path_match.group("approval"):
        raise MergeAuthorizationError("approval_id_mismatch")
    if not isinstance(document.get("gate"), str) or not re.fullmatch(r"G[1-7]_[A-Z_]+", document["gate"]):
        raise MergeAuthorizationError("approval_gate_invalid")
    if document.get("decision") != "approved":
        raise MergeAuthorizationError("approval_decision_invalid")
    if not isinstance(document.get("actor_id"), str) or len(document["actor_id"]) < 3:
        raise MergeAuthorizationError("approval_actor_invalid")
    if not isinstance(document.get("actor_role"), str) or not document["actor_role"]:
        raise MergeAuthorizationError("approval_role_invalid")
    if not isinstance(document.get("decided_at"), str) or "T" not in document["decided_at"]:
        raise MergeAuthorizationError("approval_time_invalid")
    evidence_ids = document.get("evidence_ids")
    if (
        not isinstance(evidence_ids, list) or not evidence_ids
        or any(not isinstance(value, str) or not value for value in evidence_ids)
        or len(evidence_ids) != len(set(evidence_ids))
    ):
        raise MergeAuthorizationError("approval_evidence_invalid")
    if not set(evidence_ids).issubset(known_evidence_ids):
        raise MergeAuthorizationError("approval_evidence_missing")
    gate_policy = policy.get("gate_policy")
    if not isinstance(gate_policy, dict) or document["gate"] not in gate_policy:
        raise MergeAuthorizationError("approval_gate_not_allowed")
    gate_rule = gate_policy[document["gate"]]
    if (
        not isinstance(gate_rule, dict) or not isinstance(gate_rule.get("roles"), list)
        or document["actor_role"] not in gate_rule["roles"]
    ):
        raise MergeAuthorizationError("approval_role_not_allowed")
    provider = document.get("identity_provider")
    trusted_identity = policy.get("trusted_identity")
    if (
        not isinstance(provider, str) or not provider
        or not isinstance(trusted_identity, dict)
        or not isinstance(trusted_identity.get("providers"), list)
        or provider not in trusted_identity["providers"]
    ):
        raise MergeAuthorizationError("approval_provider_invalid")
    if document.get("identity_claim") is not None and not isinstance(document["identity_claim"], str):
        raise MergeAuthorizationError("approval_claim_invalid")
    _validate_sha(document.get("commit_sha"), code="approval_commit_invalid")
    return document


def _validate_request(document: Any) -> dict[str, Any]:
    if not isinstance(document, dict) or set(document) != REQUEST_KEYS:
        raise MergeAuthorizationError("request_contract_invalid")
    if document.get("schema_version") != REQUEST_VERSION:
        raise MergeAuthorizationError("request_version_invalid")
    if not isinstance(document.get("repository_id"), str) or not NUMERIC_ID_PATTERN.fullmatch(document["repository_id"]):
        raise MergeAuthorizationError("repository_id_invalid")
    _validate_positive_int(document.get("pull_request"), code="pull_request_invalid", maximum=2_147_483_647)
    _validate_sha(document.get("head_sha"), code="head_sha_invalid")
    _validate_sha(document.get("base_sha"), code="base_sha_invalid")
    base_ref = document.get("base_ref")
    if (
        not isinstance(base_ref, str) or not BASE_REF_PATTERN.fullmatch(base_ref)
        or ".." in PurePosixPath(base_ref).parts or base_ref.endswith("/")
    ):
        raise MergeAuthorizationError("base_ref_invalid")
    _validate_digest(document.get("policy_sha256"), code="policy_digest_invalid")
    _validate_digest(document.get("nonce"), code="nonce_invalid")
    _validate_window(document.get("issued_at"), document.get("expires_at"))
    classification = document.get("classification")
    protected = ("change_id", "approval_path", "approval_sha256", "target_commit")
    if classification == "not_applicable":
        if any(document.get(key) is not None for key in protected):
            raise MergeAuthorizationError("request_classification_invalid")
    elif classification == "approval":
        if not isinstance(document.get("change_id"), str) or not CHANGE_ID_PATTERN.fullmatch(document["change_id"]):
            raise MergeAuthorizationError("request_change_invalid")
        path = _validate_path(document.get("approval_path"))
        if not APPROVAL_FILE_PATTERN.fullmatch(path):
            raise MergeAuthorizationError("request_approval_path_invalid")
        _validate_digest(document.get("approval_sha256"), code="request_approval_digest_invalid")
        _validate_sha(document.get("target_commit"), code="request_target_commit_invalid")
    else:
        raise MergeAuthorizationError("request_classification_invalid")
    return document


def build_authorization_request(
    *, repository_id: str, pull_request: int, head_sha: str, base_sha: str,
    base_ref: str, files: list[dict[str, Any]], approval_content: bytes | None,
    policy: dict[str, Any], known_evidence_ids: set[str], nonce: str,
    issued_at: int, expires_at: int,
) -> dict[str, Any]:
    if not isinstance(policy, dict) or not policy:
        raise MergeAuthorizationError("policy_contract_invalid")
    if (
        not isinstance(known_evidence_ids, set)
        or any(not isinstance(value, str) or not value for value in known_evidence_ids)
    ):
        raise MergeAuthorizationError("evidence_context_invalid")
    policy_sha256 = canonical_digest(policy)
    if not isinstance(files, list) or not files or len(files) > 3000:
        raise MergeAuthorizationError("diff_file_count_invalid")
    normalized = [_validate_diff_file(item) for item in files]
    candidates = [item for item in normalized if _approval_candidate(item["path"])]
    if not candidates:
        if approval_content is not None:
            raise MergeAuthorizationError("unexpected_approval_content")
        request = {
            "schema_version": REQUEST_VERSION,
            "repository_id": repository_id,
            "pull_request": pull_request,
            "head_sha": head_sha,
            "base_sha": base_sha,
            "base_ref": base_ref,
            "classification": "not_applicable",
            "change_id": None,
            "approval_path": None,
            "approval_sha256": None,
            "target_commit": None,
            "policy_sha256": policy_sha256,
            "nonce": nonce,
            "issued_at": issued_at,
            "expires_at": expires_at,
        }
        return _validate_request(request)
    if len(normalized) != 1 or len(candidates) != 1:
        raise MergeAuthorizationError("approval_diff_not_single_purpose")
    item = candidates[0]
    match = APPROVAL_FILE_PATTERN.fullmatch(item["path"])
    if not match:
        raise MergeAuthorizationError("approval_path_invalid")
    if item["status"] != "added":
        raise MergeAuthorizationError("approval_must_be_added")
    if item["is_symlink"] or item["is_submodule"]:
        raise MergeAuthorizationError("approval_file_type_invalid")
    if not isinstance(approval_content, bytes) or not approval_content:
        raise MergeAuthorizationError("approval_content_missing")
    if len(approval_content) != item["size"]:
        raise MergeAuthorizationError("approval_size_mismatch")
    approval_digest = hashlib.sha256(approval_content).hexdigest()
    if not hmac.compare_digest(approval_digest, item["sha256"]):
        raise MergeAuthorizationError("approval_digest_mismatch")
    approval = _validate_approval_document(
        approval_content, match, policy=policy, known_evidence_ids=known_evidence_ids,
    )
    if approval["commit_sha"] != base_sha:
        raise MergeAuthorizationError("approval_target_base_mismatch")
    request = {
        "schema_version": REQUEST_VERSION,
        "repository_id": repository_id,
        "pull_request": pull_request,
        "head_sha": head_sha,
        "base_sha": base_sha,
        "base_ref": base_ref,
        "classification": "approval",
        "change_id": approval["change_id"],
        "approval_path": item["path"],
        "approval_sha256": approval_digest,
        "target_commit": approval["commit_sha"],
        "policy_sha256": policy_sha256,
        "nonce": nonce,
        "issued_at": issued_at,
        "expires_at": expires_at,
    }
    return _validate_request(request)


def _decode_key(key_b64: str) -> bytes:
    if not isinstance(key_b64, str) or not key_b64:
        raise MergeAuthorizationError("attestation_key_invalid")
    try:
        key = base64.b64decode(key_b64, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise MergeAuthorizationError("attestation_key_invalid") from exc
    if len(key) != 32 or base64.b64encode(key).decode("ascii") != key_b64:
        raise MergeAuthorizationError("attestation_key_invalid")
    return key


def _attestation_payload(attestation: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in attestation.items() if key != "signature"}


def _validate_attestation(document: Any) -> dict[str, Any]:
    if not isinstance(document, dict) or set(document) != ATTESTATION_KEYS:
        raise MergeAuthorizationError("attestation_contract_invalid")
    if document.get("schema_version") != ATTESTATION_VERSION:
        raise MergeAuthorizationError("attestation_version_invalid")
    _validate_digest(document.get("request_digest"), code="attestation_request_digest_invalid")
    if document.get("decision") not in {"approved", "denied"}:
        raise MergeAuthorizationError("attestation_decision_invalid")
    if document.get("review_policy_result") not in {"passed", "failed"}:
        raise MergeAuthorizationError("attestation_review_invalid")
    workflow = document.get("control_workflow_ref")
    if (
        not isinstance(workflow, str) or not workflow or len(workflow.encode("utf-8")) > 512
        or "\n" in workflow or "\r" in workflow or "\0" in workflow
    ):
        raise MergeAuthorizationError("attestation_workflow_invalid")
    _validate_window(document.get("issued_at"), document.get("expires_at"))
    signature = document.get("signature")
    if not isinstance(signature, str) or not re.fullmatch(r"hmac-sha256:[a-f0-9]{64}", signature):
        raise MergeAuthorizationError("attestation_signature_invalid")
    return document


def sign_attestation(
    request: dict[str, Any], *, decision: str, review_policy_result: str,
    control_workflow_ref: str, key_b64: str, issued_at: int, expires_at: int,
) -> dict[str, Any]:
    _validate_request(request)
    key = _decode_key(key_b64)
    attestation: dict[str, Any] = {
        "schema_version": ATTESTATION_VERSION,
        "request_digest": canonical_digest(request),
        "decision": decision,
        "review_policy_result": review_policy_result,
        "control_workflow_ref": control_workflow_ref,
        "issued_at": issued_at,
        "expires_at": expires_at,
        "signature": "hmac-sha256:" + "0" * 64,
    }
    _validate_attestation(attestation)
    if attestation["issued_at"] < request["issued_at"] or attestation["expires_at"] > request["expires_at"]:
        raise MergeAuthorizationError("attestation_window_outside_request")
    signature = hmac.new(
        key,
        b"SDD_MERGE_AUTHZ_ATTESTATION_V1\0" + canonical_json(_attestation_payload(attestation)),
        hashlib.sha256,
    ).hexdigest()
    attestation["signature"] = "hmac-sha256:" + signature
    return attestation


def verify_attestation(
    request: dict[str, Any], attestation: dict[str, Any], *, key_b64: str,
    current_head_sha: str, current_base_sha: str, current_policy: dict[str, Any],
    now: int,
) -> str:
    _validate_request(request)
    _validate_attestation(attestation)
    key = _decode_key(key_b64)
    _validate_sha(current_head_sha, code="current_head_invalid")
    _validate_sha(current_base_sha, code="current_base_invalid")
    if request["classification"] != "approval":
        raise MergeAuthorizationError("attestation_not_allowed")
    if request["head_sha"] != current_head_sha or request["base_sha"] != current_base_sha:
        raise MergeAuthorizationError("authorization_stale")
    if not isinstance(current_policy, dict) or canonical_digest(current_policy) != request["policy_sha256"]:
        raise MergeAuthorizationError("authorization_policy_stale")
    if isinstance(now, bool) or not isinstance(now, int) or now < request["issued_at"]:
        raise MergeAuthorizationError("verification_time_invalid")
    if now > request["expires_at"] or now > attestation["expires_at"]:
        raise MergeAuthorizationError("authorization_expired")
    if attestation["issued_at"] < request["issued_at"] or attestation["expires_at"] > request["expires_at"]:
        raise MergeAuthorizationError("attestation_window_outside_request")
    request_digest = canonical_digest(request)
    if not hmac.compare_digest(attestation["request_digest"], request_digest):
        raise MergeAuthorizationError("attestation_request_mismatch")
    expected = hmac.new(
        key,
        b"SDD_MERGE_AUTHZ_ATTESTATION_V1\0" + canonical_json(_attestation_payload(attestation)),
        hashlib.sha256,
    ).hexdigest()
    actual = attestation["signature"].split(":", 1)[1]
    if not hmac.compare_digest(actual, expected):
        raise MergeAuthorizationError("attestation_signature_mismatch")
    if attestation["decision"] != "approved" or attestation["review_policy_result"] != "passed":
        raise MergeAuthorizationError("private_review_not_approved")
    return canonical_digest(attestation)


def build_public_check_output(
    request: dict[str, Any], *, attestation: dict[str, Any] | None,
    key_b64: str | None = None, current_head_sha: str | None = None,
    current_base_sha: str | None = None, current_policy: dict[str, Any] | None = None,
    now: int | None = None,
) -> dict[str, Any]:
    _validate_request(request)
    if request["classification"] == "not_applicable":
        if (
            attestation is not None or key_b64 is not None or current_head_sha is not None
            or current_base_sha is not None or current_policy is not None or now is not None
        ):
            raise MergeAuthorizationError("unexpected_attestation")
        conclusion = "success"
        attestation_digest = None
    else:
        if (
            attestation is None or key_b64 is None or current_head_sha is None
            or current_base_sha is None or current_policy is None or now is None
        ):
            raise MergeAuthorizationError("verified_attestation_required")
        digest = verify_attestation(
            request, attestation, key_b64=key_b64,
            current_head_sha=current_head_sha, current_base_sha=current_base_sha,
            current_policy=current_policy, now=now,
        )
        conclusion = "success"
        attestation_digest = digest
    return {
        "schema_version": CHECK_VERSION,
        "check_name": CHECK_NAME,
        "conclusion": conclusion,
        "classification": request["classification"],
        "repository_id": request["repository_id"],
        "pull_request": request["pull_request"],
        "head_sha": request["head_sha"],
        "change_id": request["change_id"],
        "approval_sha256": request["approval_sha256"],
        "attestation_digest": attestation_digest,
    }


def validate_webhook_signature(body: bytes, signature_header: str, secret: bytes) -> None:
    if not isinstance(body, bytes) or not body or len(body) > MAX_WEBHOOK_BYTES:
        raise MergeAuthorizationError("webhook_body_invalid")
    if not isinstance(secret, bytes) or not secret or len(secret) > 4096:
        raise MergeAuthorizationError("webhook_secret_invalid")
    if not isinstance(signature_header, str) or not re.fullmatch(r"sha256=[a-f0-9]{64}", signature_header):
        raise MergeAuthorizationError("webhook_signature_invalid")
    expected = "sha256=" + hmac.new(secret, body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature_header, expected):
        raise MergeAuthorizationError("webhook_signature_mismatch")


class ReplayStore:
    """Private, atomic file replay store that never persists raw delivery IDs."""

    def __init__(self, root: Path):
        if not isinstance(root, Path):
            raise MergeAuthorizationError("replay_store_path_invalid")
        if root.exists() and root.is_symlink():
            raise MergeAuthorizationError("replay_store_symlink_rejected")
        root.mkdir(parents=True, exist_ok=True)
        if root.is_symlink() or not root.is_dir():
            raise MergeAuthorizationError("replay_store_path_invalid")
        self.root = root

    def claim(self, delivery_id: str, request_digest: str, *, now: int) -> str:
        if not isinstance(delivery_id, str) or not delivery_id:
            raise MergeAuthorizationError("delivery_id_invalid")
        try:
            delivery_bytes = delivery_id.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise MergeAuthorizationError("delivery_id_invalid") from exc
        if len(delivery_bytes) > MAX_DELIVERY_ID_BYTES or "\0" in delivery_id:
            raise MergeAuthorizationError("delivery_id_invalid")
        _validate_digest(request_digest, code="replay_request_digest_invalid")
        _validate_positive_int(now, code="replay_time_invalid")
        delivery_digest = hashlib.sha256(
            b"SDD_GITHUB_DELIVERY_V1\0" + delivery_bytes
        ).hexdigest()
        target = self.root / f"{delivery_digest}.json"
        if target.parent != self.root or target.is_symlink():
            raise MergeAuthorizationError("replay_store_path_invalid")
        record = {
            "schema_version": "merge-authz-replay/v1",
            "delivery_digest": delivery_digest,
            "request_digest": request_digest,
            "recorded_at": now,
        }
        try:
            descriptor = os.open(
                target,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                stat.S_IRUSR | stat.S_IWUSR,
            )
        except FileExistsError:
            if target.is_symlink():
                raise MergeAuthorizationError("replay_store_symlink_rejected")
            try:
                existing = strict_json_loads(target.read_bytes(), max_bytes=4096)
            except OSError as exc:
                raise MergeAuthorizationError("replay_store_read_failed") from exc
            if (
                not isinstance(existing, dict)
                or set(existing) != {"schema_version", "delivery_digest", "request_digest", "recorded_at"}
                or existing.get("schema_version") != "merge-authz-replay/v1"
                or existing.get("delivery_digest") != delivery_digest
            ):
                raise MergeAuthorizationError("replay_store_record_invalid")
            if existing.get("request_digest") != request_digest:
                raise MergeAuthorizationError("delivery_replay_mismatch")
            return "duplicate"
        except OSError as exc:
            raise MergeAuthorizationError("replay_store_write_failed") from exc
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
            raise MergeAuthorizationError("replay_store_write_failed") from exc
        return "new"
