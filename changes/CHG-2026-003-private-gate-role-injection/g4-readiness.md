# CHG-2026-003 G4 Implementation Readiness Decision

- Decision：Approved
- Decided At：2026-07-15 Asia/Taipei
- Baseline Commit：`6af86da7bf89cf448a86844497ae929782635834`
- Quality Gate Run：`29347540872`（success）
- Risk Level：L2

## Authorized Scope

- TASK-001：strict protected role-map parser、policy-derived resolver 與 performance test。
- TASK-002：OIDC context validator、repository-scoped HMAC pseudonym 與 security failure paths。
- TASK-003：safe Approval ID／atomic output、provider validation 與 protected workflow contract。
- TASK-004：runbook、Feature 與 privacy／pepper operating boundaries。
- TASK-006：完整 local governance、package round-trip、privacy scan、cross-platform CI 與 implementation evidence。

TASK-005 不在本次自動執行授權內；它仍需 protected GitHub Environment、真實受信任 identity、正式 Approval artifacts、Human review／merge 與 Change Manager 逐步 remediation。

## Accepted Controls

- G3 accepted SEC-F-001 trust boundary 與 ADR-001 pepper identity-root rule 持續有效。
- 只使用 synthetic actor IDs、mapping 與 pepper 進行公開測試；不讀取或建立真實 private mapping。
- 缺少、矛盾或 malformed identity input 必須 fail closed，不得 fallback 到公開 `config/github-role-map.json`。
- 不手工修改 `state.json`，不偽造 Approval、OIDC claim、commit signature 或企業角色。

## Expected Handoff

完成 TASK-001～004／006 後只能標記為 Implemented／Awaiting Verification。下一個合法 Gate 是 G5_IMPLEMENTATION；TEST-WORKFLOW-001 與 TASK-005 若仍缺 protected Environment evidence，必須列為 blocker，不得宣告 Change 完成。
