# CHG-2026-003 Release & Rollback Plan

## Release Strategy

- Strategy：Protected workflow opt-in；先以 CHG-2026-003 bootstrap，再進行 CHG-2026-002 remediation pilot。
- Window：Human administrator、Change Manager 與 Security Reviewer 可共同觀察的 maintenance window。
- Owner：Change Manager（governance）、Platform Owner（Environment）、Security Owner（private mapping／pepper）。

## Pre-release Checklist

- [ ] G5 Build／Test／Security Gate 通過
- [ ] `sdd-approval` Environment reviewers、branch protection、CODEOWNERS 已由 Human administrator 驗證
- [ ] Protected mapping／pepper 已在 Secret Store 建立，且未進 Git／log／artifact
- [ ] Success 與 failure workflow run 均已演練
- [x] Rollback trigger／procedure 已定義

## Deployment Runbook

1. 依 `docs/governance/18_Enterprise_Pilot_Integration_v1.3.md` 建立受保護 Environment；不修改 public placeholder map。
2. 先對 CHG-2026-003 的 G1～G4 分別產出 commit-bound artifact，逐一 Human review／merge。
3. 每次 merge 後執行 Enterprise validation；以 current timestamp、`retrospective_governance_remediation` reason 逐步 append transition。
4. CHG-2026-003 bootstrap 驗證成功後，對 CHG-2026-002 重複 G1～G4 pilot；不得 bulk jump。
5. G5～G7 依正常 policy 執行，不由 remediation 自動核准。

## Rollback Triggers

- 任一 unauthorized／multiple eligible role、OIDC context mismatch 或 provider-contract validator finding。
- workflow log／artifact／Git 發現 mapping、pepper、JWT、Token、raw actor ID、login 或 Email。
- artifact entry 數量不等於 1、Approval target 被覆寫或 event／state projection 不一致。
- Windows／Linux package checksum 不一致或 full governance baseline 非 0。

## Rollback Procedure

1. 停用 `SDD Gate Approval` workflow／Environment，禁止產生或合併新 artifact。
2. Revert workflow／scripts 到上一個核准版本；不得 fallback 到 public login mapping。
3. 由 Secret custodian 移除或輪替 private secrets；值不得寫入 rollback ticket。
4. 保留已合併 Approval／Event，不刪除、不回填；以新的 forward-fix Change 處理格式或狀態。
5. 重新執行 Enterprise、event-chain、privacy、package 與 portability validation。

## Post-release Verification

- Smoke Test：合法 synthetic/private fixture 只產生一個 schema-valid artifact；missing mapping、spoofed workflow ref 與 existing target 全部非 0 且無 artifact。
- Observation Window：bootstrap 與 pilot 各至少完整觀察一輪 workflow、PR merge、Enterprise validation 與 state transition。
