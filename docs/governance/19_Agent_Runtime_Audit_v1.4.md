# Agent Runtime Audit v1.4

## 目的

每次 Agent 執行都必須產生可驗證、可遮罩、可轉為 Gate Evidence 的稽核包。Runtime Audit 不保存原始 Secret、API Key、Bearer Token、Password 或電子郵件。

## 稽核包

```text
reports/runs/<RUN-ID>/
├── run.json
├── context-manifest.json
├── tool-events.jsonl
├── guardrail-events.jsonl
└── final-output.json
```

- `run.json`：Change、Task、Agent、Provider、Model、Instruction、狀態與用量。
- `context-manifest.json`：Context URI、資料分類與 SHA-256，不複製原始 Context。
- `tool-events.jsonl`：工具、動作、政策決策、request/response hash 與延遲。
- `guardrail-events.jsonl`：Guardrail 結果、subject hash 與理由。
- `final-output.json`：經敏感資料遮罩的標準輸出。

## 驗證與 Evidence

```text
python scripts/run_agent_evals.py --change-id CHG-2026-001
python scripts/validate_runtime_audit.py
python scripts/run_to_evidence.py --run RUN-... --change CHG-2026-001
```

Evidence promotion 會：

1. 確認 Run 已進入 terminal state。
2. 驗證 Run 所屬 Change。
3. 對 `run.json` 計算 SHA-256。
4. 建立 Evidence JSON。
5. 在 hash-chained Event Store 追加 `EVIDENCE_ADDED`。

## 保存政策

- CI Runtime Bundle 預設保存 30 日。
- 正式升級為 Evidence 的 Run 必須移至公司不可變 Artifact Store，不能在清理時刪除。
- 未升級為 Evidence 的本機 Eval Run、latest report、cache 與 `.venv` 均為可重建暫存物。
