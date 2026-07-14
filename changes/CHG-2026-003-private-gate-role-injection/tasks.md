# CHG-2026-003 Task Breakdown

| Task ID | Requirement | 描述 | Dependency | Owner | Evidence | Status |
|---|---|---|---|---|---|---|
| TASK-001 | REQ-ROLE-MAP-001, REQ-GATE-RESOLVE-001, NFR-PERF-003 | 實作 `gate_identity.py` strict mapping、policy intersection、resolver CLI 與 benchmark | G4 approved | Engineer | TEST-ROLE-001～003, TEST-PERF-001 | Planned |
| TASK-002 | REQ-PRIVATE-ACTOR-001, SEC-IDENTITY-002, ADR-001 | 實作 OIDC context validator、repository-scoped HMAC pseudonym、pepper contract 與 failure paths | TASK-001 | Security Reviewer | TEST-IDENTITY-001～002, TEST-SECURITY-001 | Planned |
| TASK-003 | REQ-GATE-WORKFLOW-001, SEC-IDENTITY-002, SEC-PRIVACY-002, OPS-REL-003 | 實作 safe Approval ID／atomic output，更新 protected Environment workflow、safe inputs、cleanup 與 single-artifact contract | TASK-001, TASK-002 | Engineer | TEST-WORKFLOW-001～002, TEST-SECURITY-001, TEST-PRIVACY-001 | Planned |
| TASK-004 | FEAT-002, ADR-001 | 更新 private deployment runbook、Feature、ADR 與 public placeholder／pepper rotation 邊界 | TASK-003 | Product Owner | Documentation review | Planned |
| TASK-005 | REQ-STATE-REMEDIATION-001, OPS-REL-003 | 先 bootstrap CHG-2026-003，再以 CHG-2026-002 演練正式 Approval merge 與逐步 append-only state remediation | TASK-006, protected Environment ready, Human Approval merge | Change Manager | TEST-REMEDIATION-001, Enterprise validation | Planned |
| TASK-006 | All in-scope requirements | 執行完整 local governance、failure-path、package round-trip、privacy scan 與跨平台 CI，保存 implementation evidence | TASK-001, TASK-002, TASK-003, TASK-004 | QA Lead | Full baseline, Actions run, artifact hashes | Planned |

## Dependency Graph

```text
G4_READY
  -> TASK-001 role-map / resolver contract
      -> TASK-002 OIDC + pseudonym contract
          -> TASK-003 approval + workflow integration
              -> TASK-004 runbook / Feature / ADR sync
                  -> TASK-006 full verification and evidence
                      -> TASK-005 protected-environment bootstrap and remediation pilot
```

TASK-001 與 TASK-002 共用 `gate_identity.py` contract，TASK-003 同時修改 Approval validator 與 workflow trust boundary，因此不得以檔案分工名義平行實作。TASK-005 涉及 Human Approval merge 與 protected Environment，是外部治理階段，不與 code implementation 混合。

## Execution Plan

| Wave | Tasks | Entry | Exit／Handoff |
|---|---|---|---|
| 1 | TASK-001 | G4 approved；G3 baselines immutable | role parser／resolver／benchmark tests green |
| 2 | TASK-002 | TASK-001 contract green | HMAC／OIDC positive and negative fixtures green；Security Reviewer handoff |
| 3 | TASK-003 | TASK-001～002 green | provider validation、atomic Approval、safe workflow static／integration tests green |
| 4 | TASK-004 | workflow contract stable | runbook、Feature、ADR 與 public privacy boundary synchronized |
| 5 | TASK-006 | TASK-001～004 implemented | full local baseline、Windows／Linux package checksum CI、Evidence records available |
| 6 | TASK-005 | protected Environment ready；formal artifacts Human-reviewed and merged | append-only bootstrap／pilot remediation verified；no G5～G7 bypass |

## Assumptions, Risks, and Validation

- Assumption：implementation 只使用 Python 3.12+ standard library；不新增 runtime crypto dependency，依 G3 accepted SEC-F-001。
- Assumption：公開測試使用 synthetic numeric IDs、mapping 與 pepper；真實 private values 不進 workspace、Git、log 或 artifact。
- Risk：GitHub Environment／reviewers／private secrets 尚未由 repository administrator 證實可用。這不阻擋 TASK-001～004，但阻擋 TEST-WORKFLOW-001 與 TASK-005。
- Risk：前一 G3 packet 的跨平台 Actions 必須成功；未觀察成功前不得把 G4 readiness 或 deterministic package outcome 記為通過。
- Validation：每個 wave 先跑對應 failure paths；TASK-006 跑完整 AGENTS.md baseline、package build／safe verify、drift 與跨平台 CI。

## G4 Definition of Ready

- [x] G1～G3 對話決策及 review Evidence 已定義；正式 OIDC Approval／state remediation 留待新 workflow bootstrap。
- [x] Requirements、NFR、Design、ADR、Security controls、Tasks、Test Plan、Migration 與 Rollback 已定義。
- [x] 所有預計修改／新增檔案已列入 Change manifest。
- [x] Tasks 具 Requirement、Owner、Dependency、Evidence 與 bounded execution order。
- [x] 不需 Production credential；本地測試只用 synthetic fixtures。
- [ ] G3 packet commit 的 GitHub Actions Windows／Linux package jobs 與 checksum comparison 成功。
- [ ] Human G4_READY 核准。

## Parallelism Rules

只有在沒有共享 Contract、Schema、State、Migration、Runtime Resource 或未完成 Dependency 時，才可標記為可平行。
