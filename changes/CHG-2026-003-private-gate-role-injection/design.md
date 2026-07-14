# CHG-2026-003 Technical Design

- Status：Approved at G3
- Risk Level：L2
- Related Feature：FEAT-002
- Requirements Baseline：`EVD-G2-REQUIREMENTS-REVIEW`、`EVD-G2-NFR-REVIEW`

## Design Summary

本變更將 GitHub Gate identity 分成三個 fail-closed 邊界：`gate_identity.py` 負責 strict role-map、policy intersection、OIDC context validation 與 HMAC pseudonym；`prepare_gate_identity.py` 負責 workflow-safe orchestration；`create_approval.py` 只接受已縮減且符合 provider contract 的 identity context。公開 `config/github-role-map.json` 保持 placeholder，正式 workflow 不讀取該檔。

受保護 mapping 與 pepper 只注入 identity preparation step。該 step 從 GitHub OIDC endpoint 取得短期 token，驗證 claims 與不可由 workflow input 覆寫的 GitHub context，輸出 pseudonym、唯一 eligible role 及 allowlisted claim。後續 step 看不到 mapping、pepper 或 JWT，只能建立單一、commit-bound Approval JSON。

## Requirement Mapping

| Design ID | Requirement | 設計內容 |
|---|---|---|
| DES-ROLE-001 | REQ-ROLE-MAP-001, REQ-GATE-RESOLVE-001, NFR-PERF-003 | Strict protected JSON parser、policy-derived unique-role resolver、bounded input |
| DES-IDENTITY-001 | REQ-PRIVATE-ACTOR-001, SEC-IDENTITY-002 | OIDC context verification、32-byte pepper 與 repository-scoped HMAC pseudonym |
| DES-WORKFLOW-001 | REQ-GATE-WORKFLOW-001, SEC-IDENTITY-002, SEC-PRIVACY-002, OPS-REL-003 | Step-scoped secrets、safe input handling、single-artifact contract、cleanup |
| DES-APPROVAL-001 | REQ-GATE-WORKFLOW-001, SEC-IDENTITY-002 | Provider-specific actor／claim validation 與不揭露 actor 的 filesystem-safe Approval ID |
| DES-REMEDIATION-001 | REQ-STATE-REMEDIATION-001, OPS-REL-003 | 已合併 Approval 驅動的逐步 append-only remediation events |

## Current / Target Architecture

```text
Current
public github-role-map.json -> resolver(login) -> role output
GitHub OIDC JWT -----------> inline claim decode -> raw actor/login claims
                                      -> create_approval -> broad *.json artifact

Target
GitHub Environment reviewers
  -> protected SDD_GITHUB_ROLE_MAP_JSON + SDD_IDENTITY_PEPPER_B64
  -> prepare_gate_identity.py
       |- gate_identity: strict map + enterprise policy -> exactly one role
       |- GitHub OIDC response + trusted GitHub context -> verified claims
       `- HMAC(repo_id, actor_id) -> ghoidc-v1:<64 hex>
  -> safe step outputs only: pseudonym, role, reduced claim
  -> create_approval.py -> one schema-valid path
  -> validate_enterprise.py -> upload exactly that path
  -> Human-reviewed PR merge -> transition_state.py -> event_store reducer
```

## API／Event／Data Contract

### Protected role-map contract

Secret `SDD_GITHUB_ROLE_MAP_JSON` 是最大 32768 bytes 的 UTF-8 JSON：

```json
{
  "schema_version": "1.0",
  "actors": {
    "12345678": ["product_owner", "architect"]
  }
}
```

- exact top-level keys；JSON object 任何層級 duplicate key 都拒絕。
- actor key 必須符合 `[1-9][0-9]{0,19}`，總數最多 1000。
- role array 必須非空、元素唯一，且全部存在於 `enterprise-policy.json.allowed_roles`。
- Gate 必須存在；actor roles 與 Gate policy roles 交集恰為一個才成功。
- CLI `resolve_github_role.py --actor-id <numeric> --gate <gate>` 只從上述環境變數讀取 mapping；成功 stdout 只有 role，所有失敗 diagnostic 不含 actor 或 mapping 原文。

### Pseudonymous actor contract

`SDD_IDENTITY_PEPPER_B64` 必須是 canonical standard Base64，strict decode 後恰為 32 bytes。HMAC message 為：

```text
ASCII("SDD_GATE_ACTOR_V1\0")
+ UINT32_BE(len(repository_id)) + ASCII(repository_id)
+ UINT32_BE(len(actor_id))      + ASCII(actor_id)
```

輸出為 `ghoidc-v1:` 加完整 64 位 lowercase HMAC-SHA-256 hex。repository ID 與 actor ID 均須為 canonical numeric string。pepper 是 repository-level identity root，公開版本期間不可任意輪替；安全事件需輪替時，必須建立獨立 migration Change，撤銷或重新簽發未結案 Approval，避免同一人因 pseudonym 改變而重複計數。

### OIDC validation contract

`prepare_gate_identity.py` 接受 OIDC response temp file 與下列 runner-owned expected context：repository ID、actor ID、workflow ref、run ID、commit SHA。它限制 response／JWT 大小並驗證：

- JWT 三段格式、header `alg=RS256`、issuer `https://token.actions.githubusercontent.com`、audience `sdd-approval`。
- `repository_id`、`actor_id`、`job_workflow_ref`、`run_id` 分別與 GitHub context 完全一致。
- `iat`、`nbf`、`exp` 在允許 60 秒 clock skew 的有效期間，commit SHA 為 40 位 hex。
- token 是由 runner 使用 GitHub 提供的 authenticated OIDC request endpoint 經 TLS 即時取得；本地程式不宣稱另行完成 JWK signature verification。此信任邊界須由 workflow ref、Environment protection 與 GitHub runner provenance 共同限制。

縮減 `identity_claim` 為 canonical compact JSON，只允許 `identity_version`、`iss`、`aud`、`actor_ref`、`repository_id`、`job_workflow_ref`、`run_id`、`exp`；不得含 login、raw actor ID、`sub`、`jti` 或 JWT。

### Approval contract

- `create_approval.py` 對 `identity_provider=github-oidc` 強制 `actor_id` 符合 `^ghoidc-v1:[a-f0-9]{64}$`，並重新檢查 reduced claim 與 actor reference 一致。
- Approval ID 不再拼接 actor text；使用 `APR-<GATE>-ID-V1-<64 uppercase SHA256>`，digest 由 provider、actor reference、Gate 與 NUL-separated domain 決定，避免 PII、path separator、Windows reserved name 與截短碰撞。
- checkout 明確固定於觸發用的 `${{ github.sha }}`。change、gate、Evidence inputs 由 step environment 傳入並以 allowlist 解析，不將 `${{ inputs.* }}` 直接插入 shell command；Change ID 必須符合 `^CHG-[0-9]{4}-[0-9]{3,}$` 且只解析到唯一目錄，Evidence ID 必須符合 schema pattern且在 Change evidence directory 存在。
- script 成功只輸出建立的 repository-relative path；若 target 已存在或 validation 失敗，不覆寫且不留下 partial file。workflow 只 upload 該 exact path。

### Remediation event contract

`transition_state.py` 增加 allowlisted `--reason retrospective_governance_remediation`。`STATE_TRANSITIONED.payload` 保存 `from`、`to`、`evidence`、`reason`；reducer 將 reason 投影至 decision。每一步仍由當前 policy 檢查已合併 Approval，不提供 bulk jump、backdate 或 Approval bypass。

## Security & Privacy

| Threat | Control | Failure evidence |
|---|---|---|
| 公開 mapping 洩漏組織授權關係 | public placeholder；secret step scope；Kit／artifact scan | TEST-PRIVACY-001 |
| login spoofing 或 rename | 只使用 OIDC numeric actor／repository IDs | TEST-SECURITY-001 |
| malformed JSON、duplicate key、role confusion | exact schema、policy allowlist、unique eligible role | TEST-ROLE-002, TEST-ROLE-003 |
| workflow input shell injection | input 只經 env 傳遞與 schema allowlist；不做 inline interpolation | TEST-WORKFLOW-002 |
| JWT/context substitution | authenticated endpoint、issuer/audience/time/context exact match | TEST-SECURITY-001 |
| pepper／JWT 出現在 log 或 artifact | secret 最小 step scope、generic errors、temp cleanup、exact artifact path | TEST-PRIVACY-001 |
| pseudonym path 或 Approval ID injection | provider regex 與 full-digest safe Approval ID | TEST-IDENTITY-002 |
| job cancel 留下 token | `if: always()` cleanup；GitHub-hosted ephemeral runner disposal 為 hard-cancel 最終邊界 | TEST-WORKFLOW-002 |
| state history 被回寫 | append-only chain、current timestamp、reason、reducer check | TEST-REMEDIATION-001 |

GitHub Environment administrator、repository administrator 與 pepper custodian 是受信任管理角色；workflow 不自行授權這些角色。公開 Approval 只能證明由該受保護 workflow 產生，仍需 Human PR review／merge 才成為正式 repository record。

## File and Interface Impact

| File | Planned change |
|---|---|
| `scripts/gate_identity.py` | 新增 pure stdlib identity／mapping library |
| `scripts/prepare_gate_identity.py` | 新增 workflow orchestration 與 safe output writer |
| `scripts/resolve_github_role.py` | 改用 protected input 與共用 library |
| `scripts/create_approval.py` | provider contract、safe ID、atomic single-file output |
| `scripts/validate_enterprise.py` | 驗證 github-oidc pseudonym／reduced claim contract |
| `scripts/transition_state.py`, `scripts/event_store.py` | remediation reason 與 projection |
| `.github/workflows/sdd-gate-approval.yml` | step-scoped secrets、safe inputs、cleanup、exact artifact |
| tests／runbook／Feature | failure paths、部署與追溯同步 |
| `security-review.md` | 保存 G3 threat review、required controls 與 Human decisions |

## Migration & Rollback

1. G3 核准後，先完成 pure library 與 unit/security tests，再修改 workflow。
2. 建立 protected Environment secrets，但不把值寫入 Git；啟用 reviewers、branch protection、CODEOWNERS。
3. 以 CHG-2026-003 自身完成 bootstrap：新 workflow 產出當下 commit-bound G1～G4 artifacts，逐一 Human review／merge，再以 current-time remediation events 同步狀態。
4. 以 CHG-2026-002 做 pilot，依 G1→G4 產出、review、merge Approval，逐步 transition 至符合實際工作的狀態；G5～G7 維持正常流程。
5. 每一步執行 enterprise validation、event projection 與 privacy scan；任一步失敗即停止，不跨 Gate。

Rollback 採 revert workflow／scripts 到前版並停用 Environment workflow；私有 secrets 由管理員另行移除或輪替。既有 Approval／Event 不刪除、不改寫；若新格式已合併則以 forward-fix Change 處理。因公開 map 不再是正式 fallback，rollback 後 Gate workflow 預期 fail closed，而非降級為 login-based authorization。

## Alternatives

| Option | 優點 | 缺點 | 結論 |
|---|---|---|---|
| A. 真實 login／role map 提交 Git | 簡單、可直接 review | 公開授權關係與可變 login；違反 privacy boundary | Reject |
| B. GitHub login + plain SHA-256 | 無需 secret | 可由公開 login dictionary 反查，且 rename／spoofing 邊界弱 | Reject |
| C. GitHub Team API runtime lookup | 集中式管理 | 需要高權限 token、API availability 與額外外部證據 | Deferred |
| D. Protected numeric mapping + repository-scoped HMAC | 最小公開資料、deterministic、fail closed | 需 secret lifecycle 與 Environment bootstrap | Accepted at G3 |

## ADR

- `ADR-001`：Protected numeric role mapping and repository-scoped pseudonymous GitHub identity（Accepted at G3）。
