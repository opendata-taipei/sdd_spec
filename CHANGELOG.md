# Changelog

## 1.4.1 - 2026-07-13

- 將 Starter Kit 提升至 repository root，使 GitHub Actions 可直接執行。
- 新增可重建、唯讀檢查且跨平台確定排序的 Kit Manifest Gate。
- 新增 Manifest drift、runtime report 排除、唯讀、效能與公開身分資料回歸測試。
- 公開角色映射只保留 placeholder；真實 GitHub／IAM mapping 留在私有部署環境。
- 修正 pip cache dependency path 與 Linux `README.md` filename casing。
- 完成 CHG-2026-001 規格驗證 Pilot 與 GitHub Actions Linux 證據鏈。

## 1.4.0 - 2026-07-12

- 新增 Agent Runtime Audit bundle 與 Context/Tool/Guardrail schemas。
- Eval Harness 自動記錄 Provider、Model、Context hash、工具、Guardrail、用量與最終輸出。
- 新增 Secret、API key、Bearer token、Password 與 Email 遮罩。
- 新增 Runtime Audit Schema validator 與 CI Artifact 保存。
- 新增 Run-to-Evidence promotion，並追加 `EVIDENCE_ADDED` Change Event。
- 新增 Runtime Audit 完整性與敏感資料回歸測試。
- Evidence 文字檔 hash 採 LF 正規化，避免 Windows／Unix 換行差異造成誤判。
- 發布 Manifest 更新為可重建、可驗證的 v1.4.0 完整檔案清單。

## 1.3.0 - 2026-07-12

- 新增 GitHub Actions OIDC Gate Approval workflow、受保護角色映射與 CODEOWNERS。
- 新增 hash-chained append-only Change Event Store 與 state reducer。
- 狀態轉移改為 event-first，再產生 `state.json` projection。
- 新 Change bootstrap 會自動初始化 Event Store。
- 新增 OpenAI Responses API 與 Claude Messages API 的供應商中立 JSONL adapters。
- 新增 Event chain tampering 與 bootstrap 回歸測試。

## 1.2.0 - 2026-07-12

- 採用 Draft 2020-12 JSON Schema 與安全 YAML parser。
- 移除 Manifest 中重複的 status/Gate，改由 State 與 Approval Events 推導。
- 強制高風險作者/核准者、Evidence producer/approver 與互斥角色職責分離。
- 正式 Approval 必須綁定可信 Identity Provider、identity claim 與 Git commit SHA。
- 新增 CI/OIDC 驅動的 `create_approval.py`。
- 新增可插拔 JSONL Agent Eval Harness、reference adapter 與機器報告。

## 1.1.0 - 2026-07-12

- 新增供應商中立的 Enterprise Agent Control Plane。
- 新增 Gate role/minimum approval policy 與狀態前置條件。
- 新增 Evidence、Approval、Agent Run JSON contracts。
- 新增 Artifact SHA-256、Manifest/State、一致性與角色授權驗證。
- 強化狀態轉移，未取得必要 Gate Approval 時禁止前進。
- 新增 Agent governance eval baseline 與 CI 強制執行。
- 新增具核准與證據鏈的完整範例。

## v1.0

- 建立公司級 SDD Repository 結構。
- 加入 10 個工具中立 Skills。
- 加入 10 個角色型 Agents 與 Orchestrator。
- 加入標準、快速、緊急三種工作流。
- 加入 Human-in-the-loop Gate、Execution State 與 Handoff Contract。
- 加入 SDD 驗證、Drift Check 與 AI 可攜性檢查腳本。
- 加入 GitHub PR、Issue、CODEOWNERS 與 CI 範例。
