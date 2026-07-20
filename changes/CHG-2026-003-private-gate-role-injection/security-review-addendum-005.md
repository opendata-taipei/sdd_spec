# CHG-2026-003 Security Review Addendum 005：Device-Flow Private Authorizer

- Status：Required controls accepted for TASK-010 synthetic sandbox only — 2026-07-17
- Date：2026-07-17
- Risk：L3
- Inputs：Requirement Addendum 002、Design Addendum 005、ADR-003
- Mode B：Fail Closed

## Findings

| ID | Severity | Finding | Required Control |
|---|---|---|---|
| SEC-F-017 | Critical | managed controller或App private key compromise可直接偽造required check。 | dedicated hardened host、least privilege installation、secret store、artifact/config digest、rotation/revocation與independent host review。 |
| SEC-F-018 | High | device code可被phishing、remote prompt或session substitution利用。 | code只由local controller顯示；Human自行開trusted GitHub URL；每decision新session、短expiry、state/request digest binding；拒絕unsolicited code。 |
| SEC-F-019 | High | controller若只驗證GitHub login或public review，無法證明private role與self-review separation。 | fresh numeric `/user` ID、private mapping、PR author numeric comparison、Approval pseudonym comparison、unique role。 |
| SEC-F-020 | High | polling與Human authorization期間head/base/policy可能改變，造成TOCTOU。 | authorization前後fresh-read；attestation綁exact request；任何change要求新device flow。 |
| SEC-F-021 | High | user／installation token、device code或private mapping殘留在host log、swap、crash dump或shell history。 | memory-only bounded lifetime、redaction、no CLI secret args、dump禁用、encrypted swap/storage、privacy scan。 |
| SEC-F-022 | Medium | manual invocation、duplicate poll或audit outage可能造成replay／不可追溯decision。 | deterministic request key、nonce、idempotency store、private tamper-evident audit；audit unavailable即拒絕。 |

## Review Outcome

設計已獲Human授權作TASK-010 synthetic sandbox implementation，但未獲production或independent sign-off。尚未證明dedicated host、Secret Custodian、operator／authorizer separation或device-flow phishing controls可用；SEC-F-013與SEC-F-017皆為Critical且未關閉。

## Human Decision Required

2026-07-17 Human Decision接受本Addendum required controls，僅授權TASK-010 synthetic sandbox。不得把目前interactive developer workstation視為dedicated trusted host，不得在本機產生或下載App private key，不得啟用public production ruleset或formal Approval merge；SEC-F-013、016～022保持Open。
