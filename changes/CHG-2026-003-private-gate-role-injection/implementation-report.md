# CHG-2026-003 Implementation Report

- Status：Implemented — Awaiting External Verification
- Date：2026-07-15
- Feature：FEAT-002
- Design Baseline：G3 Design、ADR-001、Accepted Design Addendum 001
- Authorized Gate：G4_READY human decision

## Completed Scope

| Task | Requirements | Result |
|---|---|---|
| TASK-001 | REQ-ROLE-MAP-001, REQ-GATE-RESOLVE-001, NFR-PERF-003 | Implemented；strict protected parser、policy-derived resolver、32 KiB／100-run performance checks |
| TASK-002 | REQ-PRIVATE-ACTOR-001, SEC-IDENTITY-002, ADR-001 | Implemented；canonical 32-byte pepper、length-delimited HMAC、standard `workflow_ref` OIDC validation |
| TASK-003 | REQ-GATE-WORKFLOW-001, SEC-IDENTITY-002, SEC-PRIVACY-002, OPS-REL-003 | Implemented locally；safe dispatch inputs、step-scoped secrets、atomic Approval、exact artifact、cleanup、provider validator |
| TASK-004 | FEAT-002, ADR-001 | Implemented；Environment／artifact handoff／rotation／rollback runbooks synchronized |
| TASK-006 | All | Local verification passed；cross-platform CI pending at report creation |

TASK-005 尚未執行，因它需要 Human administrator 提供 protected Environment、真實 private mapping／pepper、正式 OIDC Approval artifacts 與 PR merge。Agent 未讀取、建立或輸出這些 private values。

## Key Implementation Decisions

- 公開 `config/github-role-map.json` 不再是正式 resolver input；缺少 `SDD_GITHUB_ROLE_MAP_JSON` 直接 fail closed。
- GitHub login 不作授權主鍵。OIDC numeric actor／repository IDs 只在受保護 step 內使用，公開 record 保存 `ghoidc-v1:<full HMAC>`。
- Accepted Addendum 001 使用 GitHub 標準 `workflow_ref`；reusable-only `job_workflow_ref` 不作 fallback。
- Approval ID 使用 provider／pseudonym／Gate domain-separated full SHA-256，filename 不含 actor reference、colon 或 path-unsafe text。
- Approval 寫入採 same-directory temporary file、fsync、hard-link no-replace 與 cleanup；既有 target 不覆寫。
- remediation transition 只新增 allowlisted `retrospective_governance_remediation` reason，不提供 bulk jump 或 backdate。

## Verification Results

- `python -m unittest discover -s tests -v`：42 tests passed。
- SDD／Enterprise validation：0 errors、0 warnings。
- Eval baseline：4 cases、0 errors；Agent eval：4/4 passed。
- Runtime audit：9 runs、0 errors。
- Pre-report Manifest：250 files valid；Portability：0 violations；Drift：PASS；event-derived state matches。
- Compileall 與 `git diff --check`：pass。
- Local deterministic package build／safe verify／governance round trip：250 entries，pre-evidence smoke archive SHA-256 `055a5e3bc2339487527cfc8bd5939bf3e4631af6df4b6420723d8e6b7aada44a`。

## Known Limits and Blockers

- TEST-WORKFLOW-001 的真實 protected Environment／OIDC artifact 尚未執行。
- TEST-WORKFLOW-002 的 GitHub cancellation cleanup log 與 TEST-PRIVACY-001 的真實 Actions log／artifact inspection 尚未保存。
- TASK-005 的 CHG-2026-003 bootstrap 與 CHG-2026-002 remediation pilot 尚未執行。
- 正式 Event-derived state 因尚無 merged OIDC Approval 仍維持 DRAFT；沒有手工修改或偽造 transition。

## Rollback and Handoff

Rollback 為停用 workflow／Environment並 revert 本 Change 的 workflow、identity／approval scripts、validator 與 runbook；不得 fallback 到 public mapping。已合併的 Approval／Event 保持不可變，格式問題以 forward-fix Change 處理。

完成 cross-platform CI 後保存獨立 CI Evidence。其後由 Human administrator 依 release plan 執行 protected Environment negative／positive runs；在外部證據與 TASK-005 完成前，不得送 G5 或宣告 Change 完成。
