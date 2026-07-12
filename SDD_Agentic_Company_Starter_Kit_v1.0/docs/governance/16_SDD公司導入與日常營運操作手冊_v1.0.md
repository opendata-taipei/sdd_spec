# SDD 公司導入與日常營運操作手冊

> 文件狀態：草案（Draft）  
> 版本：1.0  
> 文件擁有者：[公司名稱／部門]

## 1. 目的與成功定義

本手冊是文件 01～15 的執行入口。SDD 導入不是增加文件數，而是建立「權威規格 → 受控執行 → 獨立驗證 → Living Spec 同步」的閉環。成功必須包含需求品質、跨人員／跨 AI 可攜性、工程追溯、發布安全、知識持續性與合理治理成本。

## 2. 文件體系

01 政策、02 AI 與資料安全、03 Constitution、04 Proposal、05 Requirements、06 Design、07 Tasks、08 ADR、09 Test、10 Release／Rollback、11 RACI、12 Review、13 PR、14 DoR、15 DoD、16 操作手冊。權威順序為：公司政策與法規 > Constitution > Living Specs > 核准 Change 文件 > AI 建議與聊天。

## 3. 導入治理

指定 Executive Sponsor、Steering Committee、SDD Process Owner、Pilot Team、專業 Gate Owner 與 Tooling／Platform Team。AI 不具核准權。

## 4. 導入前準備

確認範圍與資料分級、指派 RACI、核准核心政策、選 Pilot、建立 Repo／權限、核准 AI 工具、完成訓練、設定 CI 與 KPI。

## 5. 試行選擇

選擇 4～8 週可完成、L2 或可控 L3、具測試與回復能力且團隊願意投入的真實 Change；第一次不建議使用 L4 核心交易或不可逆遷移。

## 6. 12 週路線圖

第 1 週啟動；第 2～3 週建立最小制度；第 3～4 週訓練；第 5～8 週執行 Pilot；第 9～10 週 PIR 與修訂；第 11～12 週擴大部署。

## 7. Change SOP

Intake／Classification → Proposal → Requirements → Design／ADR → Tasks／Test → Implement → Verify → Drift／Living Spec Sync → Release → Closure。每個 Gate 以 DoR、審核清單與證據判定。

## 8. AI 工具中立

Normative 規範層不得綁定 AI；Adapter 層可存放 CLAUDE.md、Cursor Rules、ChatGPT Instructions 等工具設定。更換人員或 AI 時，僅使用正式文件與 Repo 執行 Context Rehydration 測試。

## 9. Repository

建議目錄：/docs/governance、/docs/adr、/specs、/changes、/adapters、CI 目錄及 evidence store。每個 Change 應包含 proposal、requirements、design、tasks、test、release、execution-state、closure。

## 10. Git／CI/CD

Branch 與 Commit 含 Change／Requirement ID；PR 必須含 Scope、Test、Risk、Rollback 與 Spec Sync；設定 CODEOWNERS、Spec Lint、Traceability、Build／Test／Security、Drift 與 Release Gate。

## 11. 訓練

所有角色需完成基礎課程與端到端案例；PO／BA 練習可測試需求，Architect 練習 Design／ADR，Developer 練習受控實作，QA 練習獨立測試，Security／SRE 練習風險與回滾。

## 12. 營運節奏

每個 Change 執行 Gate；每日更新執行狀態；每週 Clinic；每 Sprint 檢討；每月 Steering KPI；每季抽樣稽核；每年政策重核。

## 13. KPI

建議追蹤 First-pass Rate、Lead Time、Rework、Unspeced Drift、Requirement-Test Coverage、Defect Escape、Rollback Readiness、Living Spec Freshness、AI Portability 與 Process Overhead。

## 14. 稽核與證據

抽查權威來源、追溯、AI 資料安全、Gate、Drift、Living Spec、Release 與 Rollback。聊天預設不是權威規格；若作證據，須保存工具版本、來源與人工審查。

## 15. 例外與緊急變更

Emergency 可先修復，但不得省略授權、操作紀錄、最小測試、監控與回復能力；應在公司規定時限內補 Change、PIR、測試與 Living Spec。

## 16. Pilot 結案

只有在流程跑通、品質達標、跨人員／跨 AI 可續作、治理成本合理、角色與工具就緒且改善 Backlog 有 Owner 時，才擴大部署。

## 17. 90 天計畫

Day 1～15 建立授權與基準；16～30 建立最小治理；31～60 Pilot；61～75 Release／Closure／Rehydration；76～90 評估與擴大。

## 18. 最終原則

規格是可攜、可審核、由公司控制的權威來源；AI 是可替換且受控的執行者。不同 AI 不必產生逐字相同程式碼，但必須滿足相同需求、契約、安全、測試與治理 Gate。
