# ADR-001：Protected Numeric Role Mapping and Pseudonymous Gate Identity

- Status：Proposed
- Date：2026-07-14
- Decision Owners：Architect、Security Owner
- Related Change：CHG-2026-003

## Context

公開 Starter Kit 不能保存企業真實 GitHub login／role mapping，但 Gate Approval 必須可將可信 identity、合法 role、Evidence 與 commit 綁定。login 是可變且可由公開資料反查的識別值，也不適合作為長期授權主鍵。

## Decision Drivers

- 公開 repository 與 artifact 的資料最小揭露。
- 對 actor rename、role confusion、mapping 缺失與 malformed input fail closed。
- Approval 在相同 repository 內可穩定識別同一核准者，以執行 minimum approvals 與 separation of duties。
- Python 3.12 standard library 可重現，不新增 runtime dependency。

## Options

| Option | Benefits | Costs / Risks |
|---|---|---|
| 公開 login mapping | 實作最少 | 洩漏授權關係、識別值可變 |
| login 的 plain hash | 不需 secret | dictionary attack 可反查 |
| Runtime GitHub Team API | 集中管理 | 高權限 token、外部 API 與稽核依賴 |
| Protected numeric mapping + HMAC pseudonym | 授權主鍵穩定、公開資料最少、可離線驗證格式 | 需管理 mapping、pepper 與 rotation procedure |

## Proposed Decision

正式 GitHub Gate workflow 只從 protected runtime JSON 以 numeric GitHub actor ID 解析 role；公開 `config/github-role-map.json` 不作正式 fallback。公開 Approval 使用 32-byte protected pepper、numeric repository ID 與 actor ID 產生完整 HMAC-SHA-256 pseudonym，格式為 `ghoidc-v1:<64 lowercase hex>`。

pepper 在 repository release lineage 中視為 identity root；正常操作不輪替。安全事件的 rotation 必須由獨立 Change 管理未結案 Approval migration，不能在同一 Gate 計數期間靜默替換。

## Consequences

### Positive

- 公開 Kit 不需要真實 login、Email 或 private role map。
- 相同 repository 內可穩定執行 unique actor 與職責分離檢查。
- mapping、pepper、OIDC 或 context 任一錯誤都能 fail closed。

### Negative / Debt

- 導入者必須維護 GitHub Environment、numeric mapping 與 pepper custody。
- pseudonym 無法由公開資料直接對應真人；受權審計需由私有 IAM overlay 完成。
- pepper rotation 是治理 migration，而非透明設定更新。

## Revisit Conditions

- GitHub 提供可公開驗證且 privacy-preserving 的 stable subject contract。
- 導入企業改採 centralized IAM／Team API 並能提供等效 immutable evidence。
- HMAC／pepper custody 的公司密碼政策改變。
