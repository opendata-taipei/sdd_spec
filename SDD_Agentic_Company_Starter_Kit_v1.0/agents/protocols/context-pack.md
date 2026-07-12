# Context Pack

推薦每次 Agent 啟動依序載入：

1. `constitution/project-constitution.md`
2. `constitution/ai-execution-contract.md`
3. `specs/living/_index.yaml` 與本 Change 相關 Living Specs
4. `changes/<ID>/manifest.yaml`
5. `proposal.md`、`requirements.md`、`nfr.md`
6. `design.md`、相關 ADR
7. `tasks.md`、`test-plan.md`
8. `state.json`
9. Git Diff、最新 Test／Scan Result

Context Pack 應採最小必要原則，避免將不相關的客戶資料、Secret 或整個歷史聊天載入 Agent。
