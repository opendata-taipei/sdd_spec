# Agent Assurance Evals

`evals/` 是供應商中立的 Agent 回歸評測層。每次修改 Agent、Skill、Prompt、Model 或 Tool Policy 時，都必須執行基線評測。

最低評測面向：需求追溯、未授權工具使用、範圍擴張、Prompt Injection、敏感資料洩漏、正確人工升級及輸出契約遵循。

執行：

- `python scripts/run_evals.py`：驗證案例契約。
- `python scripts/run_agent_evals.py`：以 reference adapter 執行決策回歸。
- `python scripts/run_agent_evals.py --adapter-command "<company adapter command>" --adapter-id "<version>"`：執行 Claude、OpenAI、Codex 或內部 Agent。

Adapter 使用 JSONL stdin/stdout。輸入是完整 eval case，輸出至少包含 `case_id` 與 `decision`；共用案例格式不得因供應商而改變。報告輸出至 `reports/evals/latest.json`。
