# CHG-2026-002 Task Breakdown

| Task ID | Requirement | 描述 | Dependency | Owner | Evidence | Status |
|---|---|---|---|---|---|---|
| TASK-001 | REQ-PACKAGE-001, OPS-REL-002 | 實作 canonical content、deterministic ZIP 與兩個 sidecars | G1-G3 approved | Engineer | TEST-PACKAGE-001, TEST-PACKAGE-002, TEST-PACKAGE-007 | Implemented |
| TASK-002 | REQ-PACKAGE-VERIFY-001, SEC-PACKAGE-001 | 實作 streaming safe verify、資源上限與攻擊 fixture | TASK-001 | Security Reviewer | TEST-PACKAGE-003, TEST-PACKAGE-004, TEST-PACKAGE-008 | Implemented |
| TASK-003 | REQ-PACKAGE-PORTABLE-001, NFR-PERF-002 | 實作無 `.git` round-trip 與效能測試 | TASK-001, TASK-002 | QA | TEST-PACKAGE-005, TEST-PACKAGE-006 | Implemented |
| TASK-004 | FEAT-001 | 建立 Feature index、使用／升級／rollback 文件 | None | Product Owner | Documentation review | Implemented |
| TASK-005 | REQ-PACKAGE-001 | 將 package build／verify／artifact upload 加入 CI | TASK-001, TASK-002 | Engineer | GitHub Actions run | Implemented |

## Parallelism Rules

只有在沒有共享 Contract、Schema、State、Migration、Runtime Resource 或未完成 Dependency 時，才可標記為可平行。
