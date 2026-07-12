# SYS-SEC-001 Security Baseline

- Authentication：`<機制>`
- Authorization：`<RBAC/ABAC>`
- Data Classification：`<等級>`
- Encryption in Transit：必要。
- Encryption at Rest：依資料分類。
- Audit Log：安全敏感操作必須記錄 Actor、Action、Target、Result、Timestamp。
- Secret：只能透過核准 Secret Store 注入。
- Dependency／Container／SAST 掃描：依 Quality Gate 執行。
