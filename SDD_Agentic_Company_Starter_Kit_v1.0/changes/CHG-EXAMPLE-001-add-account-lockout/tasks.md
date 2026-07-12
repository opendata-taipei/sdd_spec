# CHG-EXAMPLE-001 Task Breakdown

| Task ID | Requirement | 描述 | Dependency | Owner | Evidence | Status |
|---|---|---|---|---|---|---|
| TASK-001 | REQ-AUTH-001 | 實作失敗次數與鎖定狀態 | None | Developer | TEST-AUTH-001 | Ready |
| TASK-002 | SEC-AUTH-001 | 統一登入錯誤回應，避免洩漏帳號存在性 | TASK-001 | Developer | TEST-AUTH-002 | Ready |
| TASK-003 | REQ-AUTH-001, SEC-AUTH-002 | 新增管理者解鎖與 Audit Log | TASK-001 | Developer | TEST-AUTH-003 | Ready |
| TASK-004 | NFR-AUTH-001 | 建立登入效能基準與增量測試 | TASK-001 | QA | TEST-AUTH-004 | Ready |
| TASK-005 | OPS-AUTH-001 | 建立儲存失敗時 fail-closed 與告警 | TASK-001 | Developer | TEST-AUTH-005 | Ready |
