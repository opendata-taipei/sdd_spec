# Context Pack — CHG-EXAMPLE-001-add-account-lockout

Generated: 2026-07-12T02:42:03.442073

---

## FILE: `constitution/project-constitution.md`

```md
# Project Constitution

> 狀態：Draft。正式導入前必須由 Product、Architecture、Security、Engineering 與 Operations 共同核准。

## 1. 專案基本資料

| 欄位 | 內容 |
|---|---|
| 專案名稱 | `<PROJECT_NAME>` |
| Repository | `<REPOSITORY_URL>` |
| Business Owner | `<NAME>` |
| Product Owner | `<NAME>` |
| Technical Owner | `<NAME>` |
| Security Owner | `<NAME>` |
| Production Owner | `<NAME>` |

## 2. 權威來源

1. 公司政策及法規。
2. 本 Project Constitution。
3. `specs/living/` 現況規格。
4. `changes/<ID>/` 已核准變更規格。
5. ADR。
6. 原始碼與自動化測試。

程式碼與規格不一致時，不得直接假設程式碼或規格其中一方正確；必須建立 Drift Finding 並由權責人判斷。

## 3. 技術與架構原則

- 所有公開介面必須版本化。
- 跨服務整合必須有明確 Contract、Timeout、Retry、Idempotency 與錯誤模型。
- Database Schema 變更必須有 Migration、Backward Compatibility 與 Rollback／Forward-fix 策略。
- Production 變更必須可觀測，至少具備 Metrics、Logs、Alerts 與 Owner。
- 不得將 Secret、Token、Password 或客戶敏感資料寫入 Git、Prompt、Log 或測試快照。
- 禁止直接以 AI 建議取代 Architecture、Security、Legal 或 Production Approval。

## 4. SDD 規則

- 每個 Standard／Major／Critical Change 必須有唯一 Change ID。
- 每項需求必須有 Requirement ID 與可驗證 Acceptance Criteria。
- 每個 Task 必須對應至少一個 Requirement 或治理工作項目。
- 每項 Requirement 必須對應測試、人工驗證或核准的例外。
- 未通過 Definition of Ready，不得開始正式實作。
- 未通過 Definition of Done，不得宣告 Change 完成。

## 5. AI Agent 規則

AI SHALL：

- 先讀取 Constitution、Living Specs、Change 文件與目前 Execution State。
- 引用 Requirement／Task／ADR ID 說明行動依據。
- 列出假設、風險、修改檔案與驗證結果。
- 在資訊不足、規格衝突或需要風險接受時停止並要求 Human Decision。
- 產生可由不同工具重現的 Handoff Package。

AI SHALL NOT：

- 自行擴大範圍、修改商業需求或降低安全控制。
- 自行核准 Proposal、Design、Security Exception、Release 或 Risk Acceptance。
- 自行讀取或輸出未授權的 Secret、客戶資料或 Production Credential。
- 只因測試通過就宣告需求完成。

## 6. Definition of Ready 摘要

- Proposal、Requirement、NFR、Design 已完成必要審查。
- 依賴、風險、資料、資安、測試、Migration 與 Rollback 已定義。
- Tasks 可執行且具備 Owner、Acceptance Evidence 與依賴關係。

## 7. Definition of Done 摘要

- Requirement、NFR 與 Acceptance Criteria 已驗證。
- Code Review、測試、安全與 Release Gate 通過。
- Living Specs、ADR、Runbook 與監控已同步。
- Drift 已處理；Closure Report 與證據已保存。

```

---

## FILE: `constitution/ai-execution-contract.md`

```md
# AI Execution Contract

本契約適用所有 AI、Agent、IDE Assistant、CLI Agent 與自動化執行器。

## 輸入優先順序

1. 公司政策與法律限制。
2. Project Constitution。
3. Living Specs。
4. 已核准 Change 文件。
5. Execution State 與 Handoff Package。
6. Git Diff、測試與掃描結果。
7. 工具專用 Prompt／Skill／Adapter。

## 每次執行前

Agent 必須輸出或保存：

- `change_id`
- `current_phase`
- `current_task`
- `requirements_in_scope`
- `authoritative_files_read`
- `assumptions`
- `risks`
- `planned_actions`

## 每次執行後

Agent 必須更新：

- 實際修改檔案。
- 測試與檢查結果。
- 未解決問題。
- 新增決策及其依據。
- 下一個合法狀態。
- 可供另一個人員或 AI 接手的 Handoff Summary。

## 必須停止的條件

- 規格互相衝突。
- 需要新增未核准範圍。
- 無法確定資料分類或資料處理合法性。
- 需要不可逆 Migration。
- 需要降低安全控制。
- 需要 Production Credential 或直接修改 Production。
- 測試結果與預期不一致且根因不明。
- 需接受 Residual Risk。

## 可攜性要求

- 正式規格不得包含某一模型未外部化的內部上下文或聊天內容。
- 工具專用指令只能存在 `adapters/`、`skills/` 或工具專用設定中。
- 所有 Gate 與完成條件必須由文件與自動化測試表示，而不是由特定 AI 的判斷表示。

```

---

## FILE: `constitution/tool-portability-standard.md`

```md
# AI／工具可攜性標準

## 目標

更換 AI 模型、供應商、IDE、CLI Agent 或人員時，應能在不存取原聊天紀錄的條件下繼續工作。

## 必須外部化的資訊

- Requirement、NFR、Acceptance Criteria。
- Design、ADR、API／Data Contract。
- Tasks、Dependency、Owner、Status。
- 修改檔案清單與 Git Commit／PR。
- 測試、掃描、部署與觀測證據。
- 假設、限制、風險、未解決問題與下一步。

## 禁止作法

- 在正式 Requirement 中引用未保存於 Repository 的過往對話。
- 只有某個 Agent 私有 Memory 知道的商業規則。
- 以工具專用 Slash Command 取代正式 Change State。
- 只保存 AI 結論，不保存證據與決策依據。

## Portability Test

另一名未參與原對話的人員或不同 AI，在只讀取 Repository 後，必須能：

1. 說明 Change 目的、範圍、非範圍及風險。
2. 找到目前階段、下一項 Task 及阻塞事項。
3. 產生與原 Requirement 一致的測試計畫。
4. 執行或審查下一步而不依賴聊天記錄。

```

---

## FILE: `specs/living/_index.yaml`

```yaml
specs:
  - id: SYS-ARCH-001
    path: architecture/system-context.md
    owner: architecture
    status: draft
  - id: SYS-SEC-001
    path: security/security-baseline.md
    owner: security
    status: draft
  - id: SYS-OPS-001
    path: operations/operational-baseline.md
    owner: operations
    status: draft

```

---

## FILE: `changes/CHG-EXAMPLE-001-add-account-lockout/manifest.yaml`

```yaml
change_id: CHG-EXAMPLE-001
title: Add Account Lockout
risk_level: L2
status: DRAFT
owner: REPLACE_ME
requirements:
  - REQ-AUTH-001
  - SEC-AUTH-001
  - NFR-AUTH-001
  - SEC-AUTH-002
  - OPS-AUTH-001
declared_files: []
quality_gates:
  G1_PROPOSAL: pending
  G2_REQUIREMENTS: pending
  G3_DESIGN: pending
  G4_READY: pending
  G5_IMPLEMENTATION: pending
  G6_RELEASE: pending
  G7_CLOSURE: pending

```

---

## FILE: `changes/CHG-EXAMPLE-001-add-account-lockout/proposal.md`

```md
# CHG-EXAMPLE-001 Change Proposal：Add Account Lockout

- Status：Draft
- Risk Level：`<L0-L4>`
- Change Owner：`<NAME>`
- Product Owner：`<NAME>`

## 問題與背景

`<為什麼需要改變>`

## 目標與成功指標

- Objective：`<...>`
- Metric：`<...>`

## 範圍

### In Scope

- `<...>`

### Out of Scope

- `<...>`

## 影響與風險

| 項目 | 影響 | 風險 | 緩解 |
|---|---|---|---|
| `<...>` | `<...>` | `<...>` | `<...>` |

## Gate G1

- [ ] Business Problem 已確認
- [ ] Scope／Out of Scope 已確認
- [ ] Risk Level 已核准
- [ ] Owner 與 Success Metric 已定義

```

---

## FILE: `changes/CHG-EXAMPLE-001-add-account-lockout/requirements.md`

```md
# CHG-EXAMPLE-001 Requirements

## Functional Requirements

### REQ-AUTH-001

- Statement：WHEN 使用者在 10 分鐘內連續登入失敗 5 次，THEN 系統 SHALL 鎖定帳號 15 分鐘。
- Priority：Must
- Acceptance Criteria：
  - AC-001：第 5 次失敗後，後續正確密碼仍不得登入，直到鎖定時間結束。
  - AC-002：系統 SHALL 寫入不含密碼的安全稽核紀錄。
  - AC-003：管理者依核准權限可手動解除鎖定。

### SEC-AUTH-001

- Statement：系統 SHALL NOT 在 UI 或 API 回應中揭露帳號是否存在。
- Priority：Must

## Traceability

| Requirement | Design | Task | Test | Status |
|---|---|---|---|---|
| REQ-AUTH-001 | DES-AUTH-001 | TASK-001 | TEST-AUTH-001 | Approved |
| SEC-AUTH-001 | DES-AUTH-002 | TASK-002 | TEST-AUTH-002 | Approved |

```

---

## FILE: `changes/CHG-EXAMPLE-001-add-account-lockout/nfr.md`

```md
# CHG-EXAMPLE-001 Non-functional Requirements

| ID | 類型 | Requirement | 驗證方式 | Threshold |
|---|---|---|---|---|
| NFR-AUTH-001 | Performance | 登入與鎖定判斷 SHALL 不使登入 API P95 增加超過 50 ms | Performance Test | P95 增量 ≤ 50 ms |
| SEC-AUTH-002 | Security | 鎖定狀態與解除操作 SHALL 寫入不可含密碼的 Audit Log | Security Review | 100% 敏感操作留痕 |
| OPS-AUTH-001 | Reliability | 鎖定狀態儲存失敗時 SHALL fail closed 並產生告警 | Failure Test | 告警於 5 分鐘內觸發 |

```

---

## FILE: `changes/CHG-EXAMPLE-001-add-account-lockout/design.md`

```md
# CHG-EXAMPLE-001 Technical Design

## Design Summary

`<技術方案摘要>`

## Requirement Mapping

| Design ID | Requirement | 設計內容 |
|---|---|---|
| DES-001 | REQ-EXAMPLE-001 | `<...>` |

## Current / Target Architecture

`<Mermaid、PlantUML 或文字架構圖>`

## API／Event／Data Contract

`<介面、Schema、Compatibility>`

## Security & Privacy

`<Threat、Control、Data Flow、Audit>`

## Migration & Rollback

`<步驟、相容期、資料驗證、回復方式>`

## Alternatives

| Option | 優點 | 缺點 | 結論 |
|---|---|---|---|
| A | `<...>` | `<...>` | `<...>` |

## ADR

- `<ADR ID 或 N/A 理由>`

```

---

## FILE: `changes/CHG-EXAMPLE-001-add-account-lockout/tasks.md`

```md
# CHG-EXAMPLE-001 Task Breakdown

| Task ID | Requirement | 描述 | Dependency | Owner | Evidence | Status |
|---|---|---|---|---|---|---|
| TASK-001 | REQ-AUTH-001 | 實作失敗次數與鎖定狀態 | None | Developer | TEST-AUTH-001 | Ready |
| TASK-002 | SEC-AUTH-001 | 統一登入錯誤回應，避免洩漏帳號存在性 | TASK-001 | Developer | TEST-AUTH-002 | Ready |
| TASK-003 | REQ-AUTH-001, SEC-AUTH-002 | 新增管理者解鎖與 Audit Log | TASK-001 | Developer | TEST-AUTH-003 | Ready |
| TASK-004 | NFR-AUTH-001 | 建立登入效能基準與增量測試 | TASK-001 | QA | TEST-AUTH-004 | Ready |
| TASK-005 | OPS-AUTH-001 | 建立儲存失敗時 fail-closed 與告警 | TASK-001 | Developer | TEST-AUTH-005 | Ready |

```

---

## FILE: `changes/CHG-EXAMPLE-001-add-account-lockout/test-plan.md`

```md
# CHG-EXAMPLE-001 Test Plan

## Entry Criteria

- [x] Requirement 與 Design 已核准
- [x] Test Environment 與 Data 可用

## Test Cases

| Test ID | Requirement | Level | Scenario | Expected | Evidence |
|---|---|---|---|---|---|
| TEST-AUTH-001 | REQ-AUTH-001 | Integration | 10 分鐘內連續登入失敗 5 次 | 帳號鎖定 15 分鐘，正確密碼仍無法登入 | reports/tests/TEST-AUTH-001.md |
| TEST-AUTH-002 | SEC-AUTH-001 | Security | 嘗試不存在與存在帳號 | API 回應不可揭露帳號是否存在 | reports/tests/TEST-AUTH-002.md |
| TEST-AUTH-003 | SEC-AUTH-002 | Integration | 管理者解除帳號鎖定 | 權限驗證成功且 Audit Log 不含密碼 | reports/tests/TEST-AUTH-003.md |
| TEST-AUTH-004 | NFR-AUTH-001 | Performance | 比較變更前後登入 API P95 | P95 增量不超過 50 ms | reports/tests/TEST-AUTH-004.md |
| TEST-AUTH-005 | OPS-AUTH-001 | Failure | 模擬鎖定狀態儲存失敗 | 系統 fail closed 並於 5 分鐘內告警 | reports/tests/TEST-AUTH-005.md |

## Exit Criteria

- [ ] 所有 Must Requirement 已通過
- [ ] 無未接受的 Critical／High Defect
- [ ] 測試證據已保存

```

---

## FILE: `changes/CHG-EXAMPLE-001-add-account-lockout/release-plan.md`

```md
# CHG-EXAMPLE-001 Release & Rollback Plan

## Release Strategy

- Strategy：`<Rolling/Blue-Green/Canary/Feature Flag>`
- Window：`<...>`
- Owner：`<...>`

## Pre-release Checklist

- [ ] Build／Test／Security Gate 通過
- [ ] Migration 已演練
- [ ] Monitoring／Alert 已啟用
- [ ] Rollback Trigger 已確認

## Deployment Runbook

1. `<...>`

## Rollback Triggers

- `<明確可量化條件>`

## Rollback Procedure

1. `<...>`

## Post-release Verification

- Smoke Test：`<...>`
- Observation Window：`<...>`

```

---

## FILE: `changes/CHG-EXAMPLE-001-add-account-lockout/state.json`

```json
{
  "schema_version": "1.0",
  "change_id": "CHG-EXAMPLE-001",
  "title": "Add Account Lockout",
  "risk_level": "L2",
  "status": "READY_FOR_IMPLEMENTATION",
  "current_phase": "TASKS",
  "current_task": null,
  "requirements_in_scope": [
    "REQ-AUTH-001",
    "SEC-AUTH-001",
    "NFR-AUTH-001",
    "SEC-AUTH-002",
    "OPS-AUTH-001"
  ],
  "authoritative_files_read": [
    "constitution/project-constitution.md",
    "changes/CHG-EXAMPLE-001-add-account-lockout/requirements.md"
  ],
  "modified_files": [],
  "tests": [],
  "decisions": [],
  "risks": [],
  "blockers": [],
  "next_step": "執行 TASK-001，先建立失敗測試",
  "updated_by": "human-or-agent-id",
  "updated_at": "YYYY-MM-DDTHH:MM:SS+08:00"
}

```
