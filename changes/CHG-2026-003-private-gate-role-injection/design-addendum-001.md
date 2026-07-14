# CHG-2026-003 Design Addendum 001：Standard Workflow Reference Claim

- Status：Accepted
- Date：2026-07-15
- Affected Design：DES-IDENTITY-001、DES-WORKFLOW-001
- Requirements：REQ-GATE-WORKFLOW-001、SEC-IDENTITY-002
- Finding：IMP-F-001

## Finding

G3 Design 指定驗證 OIDC `job_workflow_ref` 並將它保存於 reduced claim。GitHub 官方 OIDC reference 說明：`job_workflow_ref` 是 jobs using a reusable workflow 才提供的 custom claim；一般 workflow 的標準 claim 是 `workflow_ref`。

目前 `.github/workflows/sdd-gate-approval.yml` 由 `workflow_dispatch` 直接執行，不是被 caller 呼叫的 reusable workflow。若維持原 contract，正式 token 缺少 `job_workflow_ref` 時會永久 fail closed，TEST-WORKFLOW-001 無法通過。

## Superseding Detail

只 supersede Design 中 OIDC workflow-reference 欄位名稱，其他 G3 control 不變：

1. `validate_oidc_claims` SHALL 驗證標準 claim `workflow_ref` 與 runner-owned `GITHUB_WORKFLOW_REF` 完全一致。
2. reduced `identity_claim` allowlist SHALL 使用 `workflow_ref`，不使用 `job_workflow_ref`。
3. workflow 仍固定 checkout `github.sha`，並驗證 issuer、audience、repository ID、actor ID、run ID、time window 與 40-hex commit SHA。
4. 若未來改為 reusable workflow，`job_workflow_ref` 必須另開 Change 定義 caller／callee trust semantics，不得自動接受兩者之一。

此修正不改變 Requirements、Gate role、privacy classification、SEC-F-001 trust boundary、ADR-001 或 pepper lifecycle；它把設計對齊 GitHub 對目前 workflow 類型保證提供的 claim。

## Alternatives

| Option | Impact | Recommendation |
|---|---|---|
| A. 使用標準 `workflow_ref` | 最小修正；與直接 dispatch workflow contract 一致 | Accept |
| B. 新增 dispatcher wrapper 並把現有 workflow 改為 reusable | 新增 workflow、caller/callee secrets 與 Environment trust boundary，超出目前 declared design | Reject for CHG-2026-003 |
| C. 保留 `job_workflow_ref` | 正式 workflow 預期永久 fail closed | Reject |

## Verification Update

- TEST-IDENTITY-001／TEST-SECURITY-001：positive fixture 改為 `workflow_ref`；missing／spoofed `workflow_ref` 必須拒絕。
- TEST-WORKFLOW-001：真實 GitHub token 的 `workflow_ref` 與 `GITHUB_WORKFLOW_REF` exact match。
- TEST-PRIVACY-001：reduced claim 仍不得含 actor login、raw actor ID、`sub`、`jti` 或 JWT。

## Human Decision

2026-07-15 已核准 Addendum 001：以標準 `workflow_ref` supersede G3 Design 中的 `job_workflow_ref`。TASK-003 可依本 addendum 繼續；未來 reusable workflow boundary 仍須另開 Change。
