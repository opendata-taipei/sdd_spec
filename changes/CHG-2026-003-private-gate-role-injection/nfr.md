# CHG-2026-003 Non-functional Requirements

| ID | 類型 | Requirement | 驗證方式 | Threshold |
|---|---|---|---|---|
| NFR-PERF-003 | Performance | 本地 role-map parse、schema validation、actor lookup、policy intersection 與 pseudonym calculation SHALL 在固定資源上保持有界 | 32 KiB max fixture 重複 100 次 | 單次 p95 < 200 ms；process peak RSS < 64 MiB，不含 OIDC network request |
| SEC-IDENTITY-002 | Security | 授權 SHALL 只依可信 OIDC numeric actor ID、protected mapping、protected pepper 與 repository policy；任一輸入不可信或不一致時 fail closed | unit／workflow negative tests、security review | 100% failure fixtures 非 0；0 unauthorized Approval artifacts |
| SEC-PRIVACY-002 | Privacy | Git、Kit package、stdout／stderr、workflow log 與 artifact SHALL 不含真實 GitHub login、Email、raw actor ID、role map、pepper、JWT、Token 或非必要 OIDC claims | secret/PII pattern scan、artifact inspection、package test | 0 finding；Approval 僅含 pseudonym、role、最小 claims、commit 與 Evidence refs |
| OPS-REL-003 | Reliability | 缺少 protected config、OIDC failure、cancel、invalid Evidence 或 state transition failure SHALL 保持 repository state 不變且不留下可誤用的 partial Approval | failure injection、event reducer check | 0 partial repository mutation；cleanup 全部通過；重跑行為 deterministic |

## Privacy Data Classification

| Data | Classification | Persistence |
|---|---|---|
| GitHub login、numeric actor ID、private role map | Internal authorization metadata | 只存在受保護 workflow memory／secret context，不進 Git／artifact |
| HMAC pepper、OIDC JWT、GitHub token | Secret | 只存在 Secret Store／短期 process context，不落盤或輸出 |
| Repository-scoped actor pseudonym、approved role | Audit metadata | 可進 Approval record；不得提供公開 reverse mapping |
| Reduced OIDC claim、commit SHA、Evidence IDs | Audit evidence | 可進 Approval record，欄位採 allowlist |
