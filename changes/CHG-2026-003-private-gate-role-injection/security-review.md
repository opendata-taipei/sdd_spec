# CHG-2026-003 G3 Security Review

- Review Status：Pass — G3 Trust Boundaries Accepted
- Reviewed At：2026-07-14
- Risk Level：L2
- Applicable Gate：G3_DESIGN
- Inputs：approved Requirements／NFR evidence、proposed Design、ADR-001、Enterprise Policy v1.4

## Security Findings

| ID | Severity | Requirement／Design | Finding | Disposition |
|---|---|---|---|---|
| SEC-F-001 | Medium | SEC-IDENTITY-002, DES-IDENTITY-001 | 本地 stdlib validator 不做 GitHub JWT JWK signature verification；它信任 runner 透過 authenticated OIDC endpoint 與 TLS 即時取得的 response，再檢查 issuer、audience、time 與完整 GitHub context。 | Residual trust boundary；需 G3 明確接受或要求加入 cryptographic verification dependency。 |
| SEC-F-002 | Medium | REQ-PRIVATE-ACTOR-001, ADR-001 | pepper rotation 會改變 pseudonym；若在未結案 Gate 中靜默輪替，同一真人可能被視為不同 actor。 | Required control：pepper 視為 repository identity root；rotation 必須獨立 Change、停止核准並處理未結案 records。 |
| SEC-F-003 | Medium | REQ-GATE-WORKFLOW-001, DES-WORKFLOW-001 | workflow dispatch inputs 若直接插入 shell，可造成 command／path injection；現有 workflow 有此風險。 | Required control：全部經 environment 傳遞、regex allowlist、unique directory resolution；checkout pin 至 `github.sha`。 |
| SEC-F-004 | Low | SEC-PRIVACY-002, DES-WORKFLOW-001 | OIDC JWT 在 GitHub-hosted runner 需短暫落於 restrictive temp file；hard cancellation 可能跳過 cleanup step。 | Required control：`if: always()` cleanup、不得 artifact/upload；hard-cancel 以 ephemeral runner disposal 為最終清除邊界。 |
| SEC-F-005 | Low | REQ-GATE-WORKFLOW-001, DES-APPROVAL-001 | pseudonym 含 `:`，若直接用於 Approval ID／filename 會違反 schema 且破壞 Windows portability。 | Required control：Approval ID 使用 provider／actor／Gate domain-separated full SHA-256，不直接拼接 actor。 |

## Required Controls

1. `gate_identity.py` 對 bytes、actor count、duplicate JSON keys、numeric IDs、policy roles、eligible-role count 全部有界且 fail closed（REQ-ROLE-MAP-001、DES-ROLE-001）。
2. HMAC 使用 canonical 32-byte pepper、固定 domain 與 length-delimited IDs；禁止 plain hash／login fallback（REQ-PRIVATE-ACTOR-001、ADR-001）。
3. OIDC claim 必須對 runner-owned repository ID、actor ID、workflow ref、run ID、audience 與有效時間做 exact match（SEC-IDENTITY-002）。
4. Secret 只存在 identity preparation step；errors 不回顯 actor、mapping、pepper 或 JWT；只 upload exact Approval path（SEC-PRIVACY-002）。
5. `github-oidc` Approval 必須由 enterprise validator 執行 provider-specific pseudonym／reduced-claim consistency check（DES-APPROVAL-001）。
6. 所有 finding 都需有 negative regression tests；不可用移除 assertion 或 public fallback 修正失敗（TASK-001～003、TEST-ROLE-002、TEST-IDENTITY-002、TEST-WORKFLOW-002、TEST-SECURITY-001、TEST-PRIVACY-001）。
7. Remediation 僅接受已 review／merged 的正式 Approval，逐步 append event 並保留 current timestamp／reason（REQ-STATE-REMEDIATION-001）。

## G3 Human Decision

2026-07-14 G3 核准者明確接受：

1. SEC-F-001 的 GitHub-hosted runner／authenticated OIDC endpoint trust model，不增加本地 JWK signature verification dependency。
2. ADR-001 將 pepper 定義為 repository identity root，rotation 視為需獨立 Change 的中斷式 migration。

SEC-F-001／002 不是 Security Exception，而是已接受的 architecture trust boundary 與強制 operating control。任何降低 required controls、改用 public fallback 或允許未受管 pepper rotation 的實作仍須停止並重新送 Design／Security review。

## Evidence and Next Gate

- 已執行：SDD／Enterprise validators、27 unit tests、evals、runtime audit、Manifest、portability、compileall、drift、state projection，全部通過。
- 本審查是 design review，不代表新 identity implementation 已測試或可發布。
- 下一個合法 Gate：G4_READY；通過前只能完成 implementation-readiness planning，不得開始 TASK-001～TASK-006。
