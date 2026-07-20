# CHG-2026-003 Task Breakdown

| Task ID | Requirement | 描述 | Dependency | Owner | Evidence | Status |
|---|---|---|---|---|---|---|
| TASK-001 | REQ-ROLE-MAP-001, REQ-GATE-RESOLVE-001, NFR-PERF-003 | 實作 `gate_identity.py` strict mapping、policy intersection、resolver CLI 與 benchmark | G4 approved | Engineer | TEST-ROLE-001～003, TEST-PERF-001 | Implemented |
| TASK-002 | REQ-PRIVATE-ACTOR-001, SEC-IDENTITY-002, ADR-001 | 實作 OIDC context validator、repository-scoped HMAC pseudonym、pepper contract 與 failure paths | TASK-001 | Security Reviewer | TEST-IDENTITY-001～002, TEST-SECURITY-001 | Implemented |
| TASK-003 | REQ-GATE-WORKFLOW-001, SEC-IDENTITY-002, SEC-PRIVACY-002, OPS-REL-003 | 實作 safe Approval ID／atomic output，更新 protected Environment workflow、safe inputs、cleanup 與 single-artifact contract | TASK-001, TASK-002 | Engineer | TEST-WORKFLOW-001～002, TEST-SECURITY-001, TEST-PRIVACY-001 | Completed — Mode A Environment verification pass |
| TASK-004 | FEAT-002, ADR-001 | 更新 private deployment runbook、Feature、ADR 與 public placeholder／pepper rotation 邊界 | TASK-003 | Product Owner | Documentation review | Implemented |
| TASK-005 | REQ-STATE-REMEDIATION-001, OPS-REL-003 | 先 bootstrap CHG-2026-003，再以 CHG-2026-002 演練正式 Approval merge 與逐步 append-only state remediation | TASK-006, protected Environment ready, Human Approval merge | Change Manager | TEST-REMEDIATION-001, Enterprise validation | Planned |
| TASK-006 | All in-scope requirements | 執行完整 local governance、failure-path、package round-trip、privacy scan 與跨平台 CI，保存 implementation evidence | TASK-001, TASK-002, TASK-003, TASK-004 | QA Lead | Full baseline, Actions run, artifact hashes | Completed |
| TASK-007 | SEC-PRIVACY-002, OPS-REL-003 | 依 Addendum 003 修正 Kit builder 排除 top-level `tmp/`，加入 regression test並保存 SEC-F-008 remediation Evidence | Addendum 003 accepted, SEC-F-008 | Engineer / Security Reviewer | TEST-KIT-PRIVACY-001, full baseline, package round-trip | Completed — cross-platform CI run `29402752423` pass |
| TASK-008 | REQ-MERGE-AUTHZ-001, REQ-APPROVAL-PR-001, SEC-MERGE-PRIVACY-003, OPS-MERGE-REL-004, ADR-002 | 在 sandbox 建立 least-privilege GitHub App、private protected Environment、canonical attestation與 exact-head required check adapter；不得啟用 production merge | Requirement Addendum 001、Design Addendum 004、ADR-002、Security Addendum 004 approved；L3 decision與credential custody完成 | Engineer / Security Engineer | TEST-MERGE-001, TEST-MERGE-FAIL-001, TEST-MERGE-REPLAY-001 | Blocked externally — local scaffold／private repo／Environment created；SEC-F-016 plan lacks private reviewer protection；App not created |
| TASK-009 | REQ-MERGE-AUTHZ-001, REQ-APPROVAL-PR-001, SEC-MERGE-PRIVACY-003, OPS-MERGE-REL-004 | 驗證 ruleset source pinning、direct-push／stale-head enforcement、private reviewer controls、public privacy與outage fail-closed，保存可重現Evidence | TASK-008 sandbox implementation；independent Security Reviewer | QA Lead / Security Reviewer | TEST-RULESET-001, TEST-MERGE-PRIVACY-001, full baseline, sandbox evidence | Planned — Mode B remains fail closed |
| TASK-010 | REQ-DEVICE-AUTH-001, OPS-POLL-AUTHZ-005, SEC-CONTROLLER-CUSTODY-004, ADR-003 | 建立webhook-inactive GitHub App、private managed poller、per-decision device auth與attestation v2 synthetic sandbox | Addendum 002／005、ADR-003、Security Addendum 005 accepted；real App／host path另需dedicated host與role custody | Engineer / Security Engineer | TEST-DEVICE-AUTH-001, TEST-POLL-001, TEST-CONTROLLER-CUSTODY-001 | Implementing — synthetic local contract only；external host/App blocked |
| TASK-011 | REQ-DEVICE-AUTH-001, OPS-POLL-AUTHZ-005, SEC-CONTROLLER-CUSTODY-004 | 獨立驗證device phishing、separation、stale poll、token privacy、App source與host custody | TASK-010 complete；independent reviewer | QA Lead / Security Reviewer | TEST-DEVICE-SEPARATION-001, TEST-POLL-STALE-001, TEST-DEVICE-PRIVACY-001 | Planned — Mode B remains fail closed |

## Dependency Graph

```text
G4_READY
  -> TASK-001 role-map / resolver contract
      -> TASK-002 OIDC + pseudonym contract
          -> TASK-003 approval + workflow integration
              -> TASK-004 runbook / Feature / ADR sync
                  -> TASK-006 full verification and evidence
                      -> TASK-005 protected-environment bootstrap and remediation pilot
                  -> TASK-007 SEC-F-008 Kit runtime exclusion remediation
                      -> TASK-008 private merge authorization sandbox
                          -> TASK-009 independent enforcement / privacy verification
                      -> SEC-F-016 decision
                          -> TASK-010 device-flow poller alternative sandbox
                              -> TASK-011 independent device / host verification
```

TASK-001 與 TASK-002 共用 `gate_identity.py` contract，TASK-003 同時修改 Approval validator 與 workflow trust boundary，因此不得以檔案分工名義平行實作。TASK-005 涉及 Human Approval merge 與 protected Environment，是外部治理階段，不與 code implementation 混合。TASK-008／009 引入新的 merge authorization trust boundary，必須先完成 Addendum／ADR／Risk Human Decision；sandbox implementation 與 independent verification 不得由同一 actor自行核准。

## Execution Plan

| Wave | Tasks | Entry | Exit／Handoff |
|---|---|---|---|
| 1 | TASK-001 | G4 approved；G3 baselines immutable | role parser／resolver／benchmark tests green |
| 2 | TASK-002 | TASK-001 contract green | HMAC／OIDC positive and negative fixtures green；Security Reviewer handoff |
| 3 | TASK-003 | TASK-001～002 green | provider validation、atomic Approval、safe workflow static／integration tests green |
| 4 | TASK-004 | workflow contract stable | runbook、Feature、ADR 與 public privacy boundary synchronized |
| 5 | TASK-006 | TASK-001～004 implemented | full local baseline、Windows／Linux package checksum CI、Evidence records available |
| 6 | TASK-005 | protected Environment ready；formal artifacts Human-reviewed and merged | append-only bootstrap／pilot remediation verified；no G5～G7 bypass |
| 7 | TASK-007 | Addendum 003 accepted；SEC-F-008 reproduced | `tmp/` excluded、regression／full baseline／package round-trip green；Security handoff |
| 8 | TASK-008 | Addendum 001／004、ADR-002與Security review approved；L3／custody decision完成 | sandbox App／private control／attestation contract implemented；production未啟用 |
| 9 | TASK-009 | TASK-008 complete；independent reviewer available | positive／negative／privacy／outage evidence complete；Mode B activation另候Human Decision |
| 10 | TASK-010 | local contract：Addendum 002／005、ADR-003、Security Addendum 005 accepted；external path：dedicated host／custody ready | provider-neutral synthetic contract完成後，待host／App sandbox handoff；production未啟用 |
| 11 | TASK-011 | TASK-010 complete；independent reviewer available | device／poll／host／privacy Evidence complete；Mode B activation另候Human Decision |

## Assumptions, Risks, and Validation

- Assumption：implementation 只使用 Python 3.12+ standard library；不新增 runtime crypto dependency，依 G3 accepted SEC-F-001。
- Assumption：公開測試使用 synthetic numeric IDs、mapping 與 pepper；真實 private values 不進 workspace、Git、log 或 artifact。
- Risk：GitHub Environment／reviewers／private secrets 尚未由 repository administrator 證實可用。這不阻擋 TASK-001～004，但阻擋 TEST-WORKFLOW-001 與 TASK-005。
- Risk：前一 G3 packet 的跨平台 Actions 必須成功；未觀察成功前不得把 G4 readiness 或 deterministic package outcome 記為通過。
- Risk：GitHub App具有 `checks:write` 且其結果控制formal Approval merge；credential compromise可能偽造authorization。Requirement Addendum 001建議實作風險升級L3，未決定前TASK-008不得開始。
- Risk：public Environment deployment history可能揭露reviewer activity；正式reviewer與IAM mapping只允許存在private control repository／overlay。
- Blocker：private sandbox Environment實測無required reviewers／prevent self-review功能（SEC-F-016）；不得以unprotected Environment繼續TASK-008或進入TASK-009。
- Validation：每個 wave 先跑對應 failure paths；TASK-006 跑完整 AGENTS.md baseline、package build／safe verify、drift 與跨平台 CI。

## G4 Definition of Ready

- [x] G1～G3 對話決策及 review Evidence 已定義；正式 OIDC Approval／state remediation 留待新 workflow bootstrap。
- [x] Requirements、NFR、Design、ADR、Security controls、Tasks、Test Plan、Migration 與 Rollback 已定義。
- [x] 所有預計修改／新增檔案已列入 Change manifest。
- [x] Tasks 具 Requirement、Owner、Dependency、Evidence 與 bounded execution order。
- [x] 不需 Production credential；本地測試只用 synthetic fixtures。
- [x] G3 packet commit 的 GitHub Actions Windows／Linux package jobs 與 checksum comparison 成功（run `29347370543`）。
- [x] Human G4_READY 核准。

## Parallelism Rules

只有在沒有共享 Contract、Schema、State、Migration、Runtime Resource 或未完成 Dependency 時，才可標記為可平行。
