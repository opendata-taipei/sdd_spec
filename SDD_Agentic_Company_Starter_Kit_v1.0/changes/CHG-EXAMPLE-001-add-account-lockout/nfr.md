# CHG-EXAMPLE-001 Non-functional Requirements

| ID | 類型 | Requirement | 驗證方式 | Threshold |
|---|---|---|---|---|
| NFR-AUTH-001 | Performance | 登入與鎖定判斷 SHALL 不使登入 API P95 增加超過 50 ms | Performance Test | P95 增量 ≤ 50 ms |
| SEC-AUTH-002 | Security | 鎖定狀態與解除操作 SHALL 寫入不可含密碼的 Audit Log | Security Review | 100% 敏感操作留痕 |
| OPS-AUTH-001 | Reliability | 鎖定狀態儲存失敗時 SHALL fail closed 並產生告警 | Failure Test | 告警於 5 分鐘內觸發 |
