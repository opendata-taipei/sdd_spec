# Enterprise Agent Control Plane v1.2

## 目的

本控制面將 SDD 規範轉換為可機器執行、可稽核且供應商中立的治理機制。Claude、OpenAI、Codex、IDE Agent 或內部 Agent 都是 Execution Provider，不是治理權威來源。

## 六層架構

1. Governance Plane：Constitution、RACI、Risk、Exception。
2. Specification Plane：Living Specs、Change、ADR、Traceability。
3. Agent Control Plane：Agent、Skill、Workflow、Context、Model Routing。
4. Policy and Security Plane：IAM、Tool Policy、Guardrails、Data Classification。
5. Execution Plane：Model Provider、CI、MCP、Internal Tools。
6. Evidence and Assurance Plane：Approval、Evidence、Evals、Tracing、Drift、Audit。

## 強制控制

- `config/enterprise-policy.json` 是 Gate、角色、最低核准數、可信身分及狀態前置條件的機器權威來源。
- `scripts/validate_enterprise.py` 驗證 Manifest/State 一致性、角色授權、核准數、Evidence 引用及 Artifact hash。
- `scripts/transition_state.py` 在關鍵轉移前重新檢查 Gate Approval。
- `schemas/agent-run.schema.json` 定義 Agent 執行軌跡；正式平台必須保存 run、model、instruction、context、tool、guardrail、usage 與 escalation。
- `evals/` 保存跨供應商共用回歸案例；Agent、Prompt、Skill、Model 或 Tool Policy 改版不得降低已核准基線。
- Manifest 只保存靜態宣告；狀態以 `state.json` 為準，Gate 狀態由 Approval Events 即時計算，不得手動填寫。
- 正式 Approval 由 `create_approval.py` 從 CI/OIDC context 產生並綁定完整 Git commit SHA。

## 信任邊界

- Agent 可以產生建議與 Evidence，不可以產生代表人類的 Approval。
- Actor 身分必須由企業 Identity Provider 或 CI OIDC 注入。
- Secret 不得進入 Prompt、Git、Evidence 或 Trace。
- Production、不可逆資料操作、安全例外與風險接受一律需要具名人工核准。

## 導入順序

1. 將角色對映至公司 IAM 群組及 CODEOWNERS。
2. 將外部 Artifact URI allowlist 與保存期限接入 Policy Engine。
3. 接入公司 Build、Test、SAST、SCA、Container Scan 結果並產生 Evidence JSON。
4. 將 Agent runtime trace 輸出至不可變 Audit Store／OpenTelemetry Backend。
5. 以真實失敗案例擴充 eval datasets，建立各模型與版本的核准基線。
