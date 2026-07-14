# CHG-2026-003 Task Breakdown

| Task ID | Requirement | 描述 | Dependency | Owner | Evidence | Status |
|---|---|---|---|---|---|---|
| TASK-001 | REQ-ROLE-MAP-001, REQ-GATE-RESOLVE-001, NFR-PERF-003 | 實作 `gate_identity.py` strict mapping、policy intersection、resolver CLI 與 benchmark | G3 approved | Engineer | TEST-ROLE-001～003, TEST-PERF-001 | Draft |
| TASK-002 | REQ-PRIVATE-ACTOR-001, SEC-IDENTITY-002 | 實作 OIDC context validator、repository-scoped HMAC pseudonym、pepper contract 與 failure paths | TASK-001 | Security Reviewer | TEST-IDENTITY-001～002, TEST-SECURITY-001 | Draft |
| TASK-003 | REQ-GATE-WORKFLOW-001, SEC-IDENTITY-002, SEC-PRIVACY-002, OPS-REL-003 | 實作 safe Approval ID／atomic output，更新 protected Environment workflow、safe inputs、cleanup 與 single-artifact contract | TASK-001, TASK-002 | Engineer | TEST-WORKFLOW-001～002, TEST-SECURITY-001, TEST-PRIVACY-001 | Draft |
| TASK-004 | FEAT-002 | 更新 private deployment runbook、Feature、ADR 與 public placeholder／pepper rotation 邊界 | TASK-003 | Product Owner | Documentation review | Draft |
| TASK-005 | REQ-STATE-REMEDIATION-001, OPS-REL-003 | 先 bootstrap CHG-2026-003，再以 CHG-2026-002 演練正式 Approval merge 與逐步 append-only state remediation | TASK-003, TASK-004, Human Approval merge | Change Manager | TEST-REMEDIATION-001, Enterprise validation | Draft |

## Parallelism Rules

只有在沒有共享 Contract、Schema、State、Migration、Runtime Resource 或未完成 Dependency 時，才可標記為可平行。
