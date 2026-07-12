# Gate Approvals

每位核准者建立一個符合 `schemas/approval.schema.json` 的 JSON。正式環境的 `actor_id` 與 `actor_role` 必須由 CI/OIDC 身分提供者產生，不得由 Agent 自行宣告。

核准紀錄必須引用至少一項 Evidence；L3/L4 變更必須遵守職責分離。
