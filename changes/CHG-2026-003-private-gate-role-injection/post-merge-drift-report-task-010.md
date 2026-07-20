# CHG-2026-003 TASK-010 Post-Merge Drift Report

- Date：2026-07-21
- Auditor Scope：PR #3／merge commit `c48680a0451a3efad204838222f51b2ef456dbd8`
- Requirements：REQ-DEVICE-AUTH-001、OPS-POLL-AUTHZ-005、SEC-CONTROLLER-CUSTODY-004
- Task／ADR：TASK-010／ADR-003
- Mode B：Fail Closed

## Results

| Finding | Classification | Result／Action |
|---|---|---|
| DRIFT-010-001 | Tracked spec sync | Feature Acceptance Outcome只描述private Environment path，未反映已接受的Addendum 005 equivalent；本分支同步為Environment或per-decision device-flow private authorizer。 |
| DRIFT-010-002 | Blocking governance drift | `state.json`仍為DRAFT／PROPOSAL、risk L2且current task為null，與已合併的TASK-010 L3 workstream不一致。State只能由正式Approval／Event推導；不得手工修改。待TASK-005或另行核准的append-only remediation。 |
| DRIFT-010-003 | Evidence sync | PR head及main merge commit的Quality Gates均4／4 success；新增merge-commit-bound post-merge Evidence。 |
| DRIFT-010-004 | Accepted incomplete scope | TASK-010只完成provider-neutral synthetic contract；dedicated host、App registration／installation、真實device OAuth、private mapping、credential custody與platform enforcement尚未完成。 |

## Validation Mapping

- REQ-DEVICE-AUTH-001：local synthetic numeric identity、role／author separation、single-use session tests及PR／main CI通過；real device OAuth未驗證。
- OPS-POLL-AUTHZ-005：freshness、expiry、installation／controller context failure paths通過；managed poller platform run未驗證。
- SEC-CONTROLLER-CUSTODY-004：public privacy contract通過；dedicated host與private custody未提供，TEST-CONTROLLER-CUSTODY-001保持Blocked。

## Blocking Findings

1. `HUMAN_DECISION_REQUIRED`：是否另行授權dedicated managed host、explicit public sandbox repository與private role／credential custody，以完成TASK-010 external path。
2. TASK-011未授權且必須由獨立Security Reviewer／QA執行；本稽核不是其sign-off。
3. SEC-F-013、016～022保持Open；不得宣稱Mode B complete或啟用production／formal Approval merge。
4. formal Change lifecycle state drift尚未remediate；本報告不修改`state.json`、events或Approvals。

## Next Legal Step

若Human不提供external sandbox前置條件，TASK-010維持Implemented Locally／Blocked Externally。若提供，先完成private custody readiness evidence，再建立webhook-inactive App；之後另行授權TASK-011 independent verification。任何production activation、formal Approval merge或risk acceptance均需新的Human Decision。
