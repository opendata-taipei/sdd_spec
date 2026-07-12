# Generic Chat Assistant Adapter

啟動時貼入或提供：

1. `constitution/project-constitution.md`
2. `constitution/ai-execution-contract.md`
3. 本 Change 的 Context Pack
4. Agent Role 的 `AGENT.md`
5. 要執行 Skill 的 `SKILL.md`

要求 Assistant 以 `schemas/agent-output.schema.json` 欄位回覆，並將重要輸出保存回 Repository。

聊天內容不是正式紀錄；Session 結束前必須產生 Handoff Summary 並更新 `state.json`。
