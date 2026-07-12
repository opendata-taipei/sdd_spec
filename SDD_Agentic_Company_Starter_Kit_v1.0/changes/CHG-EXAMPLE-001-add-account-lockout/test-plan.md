# CHG-EXAMPLE-001 Test Plan

## Entry Criteria

- [x] Requirement 與 Design 已核准
- [x] Test Environment 與 Data 可用

## Test Cases

| Test ID | Requirement | Level | Scenario | Expected | Evidence |
|---|---|---|---|---|---|
| TEST-AUTH-001 | REQ-AUTH-001 | Integration | 10 分鐘內連續登入失敗 5 次 | 帳號鎖定 15 分鐘，正確密碼仍無法登入 | reports/tests/TEST-AUTH-001.md |
| TEST-AUTH-002 | SEC-AUTH-001 | Security | 嘗試不存在與存在帳號 | API 回應不可揭露帳號是否存在 | reports/tests/TEST-AUTH-002.md |
| TEST-AUTH-003 | SEC-AUTH-002 | Integration | 管理者解除帳號鎖定 | 權限驗證成功且 Audit Log 不含密碼 | reports/tests/TEST-AUTH-003.md |
| TEST-AUTH-004 | NFR-AUTH-001 | Performance | 比較變更前後登入 API P95 | P95 增量不超過 50 ms | reports/tests/TEST-AUTH-004.md |
| TEST-AUTH-005 | OPS-AUTH-001 | Failure | 模擬鎖定狀態儲存失敗 | 系統 fail closed 並於 5 分鐘內告警 | reports/tests/TEST-AUTH-005.md |

## Exit Criteria

- [ ] 所有 Must Requirement 已通過
- [ ] 無未接受的 Critical／High Defect
- [ ] 測試證據已保存
