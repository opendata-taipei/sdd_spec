# Enterprise Pilot Integration v1.3

## GitHub OIDC Approval

1. 保持公開 `config/github-role-map.json` 為 placeholder；真實 mapping 不得提交 Git。
2. 替換 `.github/CODEOWNERS` placeholder，啟用 branch protection 與 required review。
3. 建立受保護的 `sdd-approval` GitHub Environment，設定 reviewers。
4. 在 Environment secrets 設定 `SDD_GITHUB_ROLE_MAP_JSON` 與 32-byte key 的 canonical Base64 `SDD_IDENTITY_PEPPER_B64`；正式 contract 以 CHG-2026-003 核准設計為準。
5. 執行 `SDD Gate Approval` workflow，輸入 Change、Gate 與 Evidence IDs。
6. Workflow 取得 audience=`sdd-approval` 的短期 OIDC JWT，驗證 numeric actor／repository context，只保存 repository-scoped pseudonym 與 allowlisted claims。
7. 下載本次唯一 Approval artifact，經 Change Manager PR 合併後才成為 Repository 正式紀錄。

`id-token: write` 只允許 workflow 取得 OIDC token；實際權限仍由受保護 workflow、Environment、角色映射與 CODEOWNERS 決定。

### Protected Environment contract

`SDD_GITHUB_ROLE_MAP_JSON` 必須是單行或多行均可的 UTF-8 JSON secret，最大 32 KiB。正式值只在 GitHub Environment／企業 Secret Store 維護；以下僅是合成格式範例：

```json
{"schema_version":"1.0","actors":{"12345678":["product_owner","architect"]}}
```

- actor key 是 GitHub OIDC numeric `actor_id`，不可使用 login、Email 或 display name。
- role 只能取自 `config/enterprise-policy.json`；同一 Gate 必須恰好解析出一個 eligible role。
- `SDD_IDENTITY_PEPPER_B64` 是恰好 32 random bytes 的 canonical standard Base64。生成與保存應使用公司核准的 Secret Manager／密碼工具，不在 shell history、issue、PR、Actions log 或聊天中顯示。
- pepper 是 repository identity root；正常操作不可輪替。安全事件的 rotation 必須停止未結案核准並建立獨立 migration Change。

Workflow 會比對 OIDC 標準 `workflow_ref` 與 runner-owned `GITHUB_WORKFLOW_REF`。`job_workflow_ref` 只適用 reusable workflow，不是此直接 dispatch workflow 的 fallback。

### Approval artifact handoff

1. 以受保護 Environment 執行 workflow；inputs 只接受 canonical Change ID、policy Gate 與既有 Evidence IDs。
2. 確認 run 成功且 artifact 只有一個 `APR-<GATE>-ID-V1-<DIGEST>.json`。
3. Change Manager 在隔離目錄檢查 artifact，不複製 workflow log、OIDC response 或其他 approvals。
4. 以 PR 將該單一 JSON 放入對應 `changes/<change>/approvals/`；由 CODEOWNERS／branch protection 審查後合併。
5. 合併後執行 `python scripts/validate_enterprise.py`，再依狀態機逐步 transition。Artifact 本身不是已合併 Approval，也不授權自動 merge。

缺少 Environment secret、OIDC context mismatch、未知 Evidence、target 已存在或 validator 失敗時，workflow 必須非 0 結束且不 upload Approval。Hard cancellation 由 `if: always()` cleanup 加 GitHub-hosted ephemeral runner disposal 共同構成清除邊界。

### 身分資料最小揭露

- 公開 Starter Kit、範例與文件只能保存虛構 actor 或 placeholder，不得列出真實 GitHub login、Email、企業帳號或完整 OIDC claims。
- `config/github-role-map.json` 只提供公開 placeholder；正式 workflow 不讀取它，也不得 fallback。真實 numeric actor／role mapping 由受保護 Environment 或企業 IAM 同步注入。
- GitHub login 雖通常不是秘密，但角色映射會揭露人員、專案與核准權限關聯，應視為內部授權中繼資料並採最小揭露。
- 正式環境應優先以受保護 Team、不可變 actor ID 或企業 IAM subject 綁定權限；顯示名稱只能作為輔助資訊，不得作為唯一授權依據。
- Approval Evidence 只保存驗證所需的縮減 claims 與 commit SHA；不得保存原始 OIDC token、Access Token 或不必要的個人資料。
- HMAC pepper 是 repository identity root；不得在未結案 Gate 中靜默輪替。安全事件需用獨立 Change 管理 Approval migration。

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
