# CHG-2026-003 Security Review Addendum 004：Equivalent Merge Control

- Review Status：Required Controls Accepted — Sandbox Verification Pending
- Reviewed At：2026-07-17
- Current Change Risk：L2
- Mode B Implementation Risk：L3（HD-004-01 accepted）
- Inputs：Requirement Addendum 001、Design Addendum 004、ADR-002、Enterprise Policy v1.4
- Mode B：Fail Closed

## Threat Model

受保護資產為formal Approval merge authority、private reviewer identity／role mapping、GitHub App credentials、attestation key、exact-head authorization與audit continuity。攻擊者可能是public contributor、具有repository write權限但無Change Manager role的actor、Approval作者、遭入侵的workflow／App或能重送webhook的外部來源。

trust boundaries為GitHub public repository、GitHub App webhook controller、private control repository／protected Environment、private validator／key store，以及GitHub Checks／Rulesets API。

## Findings

| ID | Severity | Requirement／Design | Finding | Required Disposition |
|---|---|---|---|---|
| SEC-F-009 | High | REQ-MERGE-AUTHZ-001, DES-MERGE-RULESET-001 | 同名commit status／check若未鎖定expected GitHub App，write actor可能spoof required check。 | ruleset鎖定App source；sandbox以其他token建立同名status並證明merge仍blocked。 |
| SEC-F-010 | High | REQ-APPROVAL-PR-001, DES-MERGE-CHECK-001 | webhook payload、stale head或check更新與merge之間存在TOCTOU，可能將舊授權套到新diff。 | 每階段重新讀取current head／diff；attestation綁head、base、Approval digest、target commit、expiry；stale result失效。 |
| SEC-F-011 | High | SEC-MERGE-PRIVACY-003, DES-PRIVATE-CONTROL-001 | 在public repository使用真實Environment reviewers／CODEOWNERS可能透過設定、deployment或review surface洩漏IAM關係。 | reviewer與mapping只存在private control repository；public output做privacy regression scan。 |
| SEC-F-012 | Medium | OPS-MERGE-REL-004 | App／private control outage可造成治理DoS；若為可用性引入bypass會轉為未授權merge。 | fail-closed merge freeze、bounded retry、no bypass；另訂operational SLO與incident runbook。 |
| SEC-F-013 | Critical | DES-MERGE-CHECK-001, DES-MERGE-ATTEST-001 | GitHub App private key／installation token或attestation key遭竊，可偽造正式merge authorization。 | least privilege、secret manager、短期installation token、rotation／revocation、key access audit、incident drill；實作前L3 review。 |
| SEC-F-014 | High | REQ-APPROVAL-PR-001, OPS-MERGE-REL-004 | fork、mixed diff、Approval modify/delete、duplicate delivery或replay可能繞過single-purpose review與actor uniqueness。 | strict classifier、fresh API read、delivery idempotency、nonce／expiry、negative regression matrix。 |
| SEC-F-015 | Medium | SEC-MERGE-PRIVACY-003, DES-MERGE-ATTEST-001 | opaque reference、App diagnostics或private repository metadata仍可能間接識別reviewer。 | public allowlist輸出contract、去識別錯誤碼、禁止private URL／team／workflow actor；人工與自動privacy review。 |
| SEC-F-016 | High | OPS-MERGE-REL-004, DES-PRIVATE-CONTROL-001 | 2026-07-17實際建立private sandbox Environment後，GitHub UI未提供required reviewers、prevent self-review或deployment protection rules；目前plan／repository能力無法形成已核准的private Human control。 | Mode B與App activation fail closed；不得用unprotected Environment、public reviewers或bypass替代。需升級GitHub plan、改用具等效private protection的平台，或提出新的Requirement／Design Addendum與Human Decision。 |

## Required Controls Before Implementation

1. Architecture／Security／Change Manager核准Requirement Addendum 001、Design Addendum 004與ADR-002，並決定L3 reclassification。
2. GitHub App與private control資產有明確owner、credential custody、rotation、revocation、break-glass禁用與audit retention規格。
3. public ruleset無formal Approval bypass，required check expected source固定為App；App不具merge／contents write／administration權限。
4. private Environment啟用required reviewers、prevent self-review、disallow bypass；reviewer／mapping不複製到public repo。
5. canonical request／attestation schema版本化，簽章或MAC涵蓋全部security-relevant fields；比較使用constant-time primitive。
6. webhook HMAC、delivery replay、TOCTOU、fork、mixed diff、stale head、source spoof、outage與privacy tests全部有failure-path Evidence。
7. sandbox驗證完成前不啟用production Mode B、不合併正式Approval、不推進TASK-005 remediation。

## Review Outcome

Human已接受required controls、role-based credential custody baseline與L3 implementation boundary，故TASK-008 sandbox implementation可開始。SEC-F-009～016仍為Open；SEC-F-016現為external sandbox blocker。本review不構成finding closure、residual risk acceptance或production readiness。

## Next Human Decision

TASK-008完成後交由TASK-009獨立Security Reviewer／QA驗證。只有SEC-F-009～016具可重現Evidence並完成security re-review後，才能提出production Mode B activation的`HUMAN_DECISION_REQUIRED`；目前SEC-F-016阻擋external sandbox，Mode B維持fail closed。
