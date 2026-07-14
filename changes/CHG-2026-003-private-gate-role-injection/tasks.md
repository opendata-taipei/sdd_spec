# CHG-2026-003 Task Breakdown

| Task ID | Requirement | 描述 | Dependency | Owner | Evidence | Status |
|---|---|---|---|---|---|---|
| TASK-001 | REQ-ROLE-MAP-001, REQ-GATE-RESOLVE-001, NFR-PERF-003 | 實作 protected mapping parser、strict validation、policy intersection 與 resolver CLI | G1-G3 approved | Engineer | TEST-ROLE-001～003, TEST-PERF-001 | Draft |
| TASK-002 | REQ-PRIVATE-ACTOR-001, SEC-IDENTITY-002 | 實作 repository-scoped HMAC actor pseudonym 與 failure-path tests | TASK-001 | Security Reviewer | TEST-IDENTITY-001～002 | Draft |
| TASK-003 | REQ-GATE-WORKFLOW-001, SEC-IDENTITY-002, SEC-PRIVACY-002, OPS-REL-003 | 更新 protected Environment workflow、minimal claims、cleanup 與單一 artifact contract | TASK-001, TASK-002 | Engineer | TEST-WORKFLOW-001～002, TEST-SECURITY-001, TEST-PRIVACY-001 | Draft |
| TASK-004 | FEAT-002 | 更新 private deployment runbook、Feature 文件與 public placeholder 邊界 | TASK-003 | Product Owner | Documentation review | Draft |
| TASK-005 | REQ-STATE-REMEDIATION-001, OPS-REL-003 | 以 CHG-2026-002 演練正式 Approval merge 與 append-only state remediation | TASK-003, TASK-004 | Change Manager | TEST-REMEDIATION-001, Enterprise validation | Draft |

## Parallelism Rules

只有在沒有共享 Contract、Schema、State、Migration、Runtime Resource 或未完成 Dependency 時，才可標記為可平行。
