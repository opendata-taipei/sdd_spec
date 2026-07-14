from __future__ import annotations

import base64
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from gate_identity import (
    GateIdentityError,
    actor_pseudonym,
    parse_oidc_response,
    reduced_identity_claim,
    validate_oidc_claims,
    validate_reduced_identity_claim,
)

PEPPER_A = base64.b64encode(bytes(range(32))).decode("ascii")
PEPPER_B = base64.b64encode(bytes(range(1, 33))).decode("ascii")


def b64url(value: dict) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def oidc_response(claims: dict, header: dict | None = None) -> str:
    token = f"{b64url(header or {'alg': 'RS256', 'typ': 'JWT'})}.{b64url(claims)}.c2ln"
    return json.dumps({"value": token}, separators=(",", ":"))


class GateIdentityTests(unittest.TestCase):
    def claims(self) -> dict:
        return {
            "iss": "https://token.actions.githubusercontent.com",
            "aud": "sdd-approval",
            "repository_id": "111",
            "actor_id": "222",
            "workflow_ref": "example/repo/.github/workflows/sdd-gate-approval.yml@refs/heads/main",
            "run_id": "333",
            "iat": 999_900,
            "nbf": 999_900,
            "exp": 1_000_300,
            "sub": "repo:private/name:ref:refs/heads/main",
            "jti": "private-jti",
            "actor": "private-login",
        }

    def test_pseudonym_is_deterministic_and_domain_separated(self):
        first = actor_pseudonym("111", "222", PEPPER_A)
        self.assertRegex(first, r"^ghoidc-v1:[a-f0-9]{64}$")
        self.assertEqual(first, actor_pseudonym("111", "222", PEPPER_A))
        self.assertNotEqual(first, actor_pseudonym("112", "222", PEPPER_A))
        self.assertNotEqual(first, actor_pseudonym("111", "223", PEPPER_A))
        self.assertNotEqual(first, actor_pseudonym("111", "222", PEPPER_B))
        self.assertNotIn("222", first)

    def test_invalid_pepper_and_identifiers_fail_closed(self):
        invalid_peppers = ["", "not-base64", base64.b64encode(b"short").decode("ascii"), PEPPER_A.rstrip("=")]
        for pepper in invalid_peppers:
            with self.subTest(pepper=pepper):
                with self.assertRaises(GateIdentityError):
                    actor_pseudonym("111", "222", pepper)
        for repository_id, actor_id in [("", "222"), ("011", "222"), ("111", "login"), ("111", "0")]:
            with self.assertRaises(GateIdentityError):
                actor_pseudonym(repository_id, actor_id, PEPPER_A)

    def test_oidc_context_and_reduced_claim(self):
        claims = self.claims()
        _, parsed = parse_oidc_response(oidc_response(claims))
        validate_oidc_claims(
            parsed, repository_id="111", actor_id="222",
            workflow_ref=claims["workflow_ref"], run_id="333",
            commit_sha="a" * 40, now=1_000_000,
        )
        actor_ref = actor_pseudonym("111", "222", PEPPER_A)
        reduced = reduced_identity_claim(
            parsed, actor_ref, repository_id="111",
            workflow_ref=claims["workflow_ref"], run_id="333",
        )
        self.assertNotIn("private-login", reduced)
        self.assertNotIn("private-jti", reduced)
        self.assertNotIn(claims["sub"], reduced)
        self.assertNotIn('"actor_id"', reduced)
        validated = validate_reduced_identity_claim(reduced, actor_ref)
        self.assertEqual(validated["actor_ref"], actor_ref)

    def test_spoofed_or_invalid_oidc_is_rejected(self):
        base = self.claims()
        mutations = [
            ("iss", "https://evil.invalid"),
            ("aud", "wrong"),
            ("repository_id", "999"),
            ("actor_id", "999"),
            ("workflow_ref", "evil/workflow@main"),
            ("run_id", "999"),
            ("exp", 999_000),
        ]
        for key, value in mutations:
            claims = dict(base)
            claims[key] = value
            _, parsed = parse_oidc_response(oidc_response(claims))
            with self.subTest(key=key):
                with self.assertRaises(GateIdentityError):
                    validate_oidc_claims(
                        parsed, repository_id="111", actor_id="222",
                        workflow_ref=base["workflow_ref"], run_id="333",
                        commit_sha="a" * 40, now=1_000_000,
                    )
        with self.assertRaises(GateIdentityError):
            parse_oidc_response(oidc_response(base, {"alg": "none"}))
        with self.assertRaises(GateIdentityError):
            parse_oidc_response('{"value":"a.b.c","value":"d.e.f"}')

    def test_reduced_claim_is_exact_and_actor_bound(self):
        claims = self.claims()
        actor_ref = actor_pseudonym("111", "222", PEPPER_A)
        reduced = reduced_identity_claim(
            claims, actor_ref, repository_id="111",
            workflow_ref=claims["workflow_ref"], run_id="333",
        )
        document = json.loads(reduced)
        document["sub"] = "forbidden"
        with self.assertRaises(GateIdentityError):
            validate_reduced_identity_claim(json.dumps(document), actor_ref)
        with self.assertRaises(GateIdentityError):
            validate_reduced_identity_claim(reduced, "ghoidc-v1:" + "0" * 64)


if __name__ == "__main__":
    unittest.main()
