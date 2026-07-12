# {{CHANGE_ID}} Task Breakdown

| Task ID | Requirement | 描述 | Dependency | Owner | Evidence | Status |
|---|---|---|---|---|---|---|
| TASK-001 | REQ-GENERIC-001 | `<實作功能需求>` | None | `<...>` | TEST-GENERIC-001 | Draft |
| TASK-002 | NFR-PERF-001 | `<驗證效能需求>` | TASK-001 | `<...>` | TEST-GENERIC-002 | Draft |
| TASK-003 | SEC-APP-001 | `<實作或驗證安全需求>` | TASK-001 | `<...>` | TEST-GENERIC-003 | Draft |
| TASK-004 | OPS-REL-001 | `<實作或驗證可靠性需求>` | TASK-001 | `<...>` | TEST-GENERIC-004 | Draft |

## Parallelism Rules

只有在沒有共享 Contract、Schema、State、Migration、Runtime Resource 或未完成 Dependency 時，才可標記為可平行。
