# CHG-EXAMPLE-001 Requirements

## Functional Requirements

### REQ-AUTH-001

- Statement：WHEN 使用者在 10 分鐘內連續登入失敗 5 次，THEN 系統 SHALL 鎖定帳號 15 分鐘。
- Priority：Must
- Acceptance Criteria：
  - AC-001：第 5 次失敗後，後續正確密碼仍不得登入，直到鎖定時間結束。
  - AC-002：系統 SHALL 寫入不含密碼的安全稽核紀錄。
  - AC-003：管理者依核准權限可手動解除鎖定。

### SEC-AUTH-001

- Statement：系統 SHALL NOT 在 UI 或 API 回應中揭露帳號是否存在。
- Priority：Must

## Traceability

| Requirement | Design | Task | Test | Status |
|---|---|---|---|---|
| REQ-AUTH-001 | DES-AUTH-001 | TASK-001 | TEST-AUTH-001 | Approved |
| SEC-AUTH-001 | DES-AUTH-002 | TASK-002 | TEST-AUTH-002 | Approved |
