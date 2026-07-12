# Enterprise Pilot Integration v1.3

## GitHub OIDC Approval

1. 將 `config/github-role-map.json` 的 placeholder 替換為企業 IAM 同步結果。
2. 替換 `.github/CODEOWNERS` placeholder，啟用 branch protection 與 required review。
3. 建立受保護的 `sdd-approval` GitHub Environment。
4. 執行 `SDD Gate Approval` workflow，輸入 Change、Gate 與 Evidence IDs。
5. Workflow 取得 audience=`sdd-approval` 的短期 OIDC JWT，只保存必要 claims，不保存原始 token。
6. 下載 Approval artifact，經 Change Manager PR 合併後才成為 Repository 正式紀錄。

`id-token: write` 只允許 workflow 取得 OIDC token；實際權限仍由受保護 workflow、Environment、角色映射與 CODEOWNERS 決定。

## Append-only Event Store

- `events.jsonl` 是變更歷史的 append-only 來源。
- 每個事件包含 sequence、previous hash 與 event hash。
- `reduce_state.py --check` 驗證事件推導結果與 `state.json` 一致。
- `transition_state.py` 先追加事件，再由 reducer 更新快照。
- `validate_enterprise.py` 會驗證 Schema、hash chain 與 state projection。

常用命令：

```text
python scripts/bootstrap_change.py CHG-2026-001 add-feature github-login
python scripts/append_event.py --change CHG-2026-001 --type EVIDENCE_ADDED --payload "{...}"
python scripts/reduce_state.py --change CHG-2026-001 --check
```

## Provider Adapter

共用契約位於 `evals/adapters/adapter-contract.json`，使用 JSONL stdin/stdout。

OpenAI：

```text
OPENAI_API_KEY=<secret>
OPENAI_MODEL=<company-approved-model>
python scripts/run_agent_evals.py --adapter-command "python evals/adapters/openai_responses_adapter.py" --adapter-id openai-pilot
```

Claude：

```text
ANTHROPIC_API_KEY=<secret>
ANTHROPIC_MODEL=<company-approved-model>
python scripts/run_agent_evals.py --adapter-command "python evals/adapters/anthropic_messages_adapter.py" --adapter-id anthropic-pilot
```

API key 只能透過 CI Secret Store 或本機環境注入，不得寫入 Git、Evidence、Event 或 Eval Report。
