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
