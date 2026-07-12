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
