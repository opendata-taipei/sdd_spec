# CHG-2026-003 TASK-008 Implementation Report：Merge Authorization Sandbox

- Status：Implemented Locally — External Sandbox Setup Pending
- Date：2026-07-17
- Risk Boundary：Mode B implementation L3
- Requirements：REQ-MERGE-AUTHZ-001、REQ-APPROVAL-PR-001、SEC-MERGE-PRIVACY-003、OPS-MERGE-REL-004
- Design／ADR：Design Addendum 004、ADR-002
- Task：TASK-008
- Mode B：Fail Closed

## Implemented Scope

- versioned JSON Schemas for canonical request與private attestation；Draft 2020-12、default additional properties rejected。
- public sandbox policy scaffold明確`production_activation=false`、expected App source placeholder、least-privilege permissions、ruleset與private Environment controls。
- Python 3.12+ standard-library merge authorization engine：
  - strict JSON／duplicate key／UTF-8／size limits；
  - single-added-Approval diff classifier與path／symlink／submodule／hash checks；
  - head、base、target commit（必須等於fresh base）、policy digest、nonce與bounded TTL binding；
  - SHA-256 webhook HMAC與constant-time compare；
  - private atomic replay store，不保存raw delivery ID；
  - domain-separated HMAC attestation與exact current-head verification；
  - public output函式內強制重驗attestation HMAC與current head/base，避免呼叫端偽造verification marker；
  - public check output allowlist，不輸出private workflow／reviewer metadata。
- GitHub App adapter contract與private sandbox runbook。
- synthetic unit／contract／failure-path／privacy tests。

## Files

- `schemas/merge-authorization-request.schema.json`
- `schemas/merge-authorization-attestation.schema.json`
- `config/merge-authorization-policy.json`
- `scripts/merge_authorization.py`
- `tests/test_merge_authorization.py`
- `adapters/github-merge-authorization/README.md`
- `docs/governance/19_Private_Merge_Authorization_Sandbox.md`

## Security Decisions

- 公開policy永遠保留App ID placeholder；實際App ID／installation、reviewer mapping與credentials只在private overlay。
- engine不含GitHub network client、不呼叫merge API、不解析private reviewer identity。
- non-Approval PR由App明確產生`not_applicable` success；Approval PR若無key與current head/base context，public output API會拒絕，且函式內部重新驗證private attestation。
- replay duplicate只在相同delivery digest與request digest時回傳idempotent result；digest不一致拒絕。

## External Work Not Yet Performed

- GitHub App尚未在private sandbox註冊／安裝。
- private repository已建立，但目前plan／UI不提供Environment reviewers、prevent self-review及protection rules（SEC-F-016）。
- public／sandbox ruleset expected-source enforcement尚未套用或驗證。
- direct push、same-name spoof、private rejection／cancellation與service outage平台runs尚未執行。

以上工作需要private administrator／Secret Custodian與sandbox details，不能從public repository推定。它們是TASK-008 external completion與TASK-009 entry blocker，不代表implementation failure，也不得以local tests取代。

### GitHub Sandbox Observation（2026-07-17）

- authenticated Settings UI仍顯示`opendata-taipei/sdd_spec`尚未建立ruleset。
- 已建立private、fork-disabled repository `opendata-taipei/sdd-merge-authorization-sandbox`，description明確標示TASK-008與no production approvals；repository尚為empty。
- 已建立Environment `sdd-merge-authorization`，未加入secret、variable或reviewer mapping。
- Environment設定頁未提供deployment protection rules、required reviewers或prevent self-review，只提供deployment branch restriction、secrets與variables。此platform／plan能力不滿足DES-PRIVATE-CONTROL-001與AC-035，記錄為SEC-F-016 High blocker。
- organization GitHub App registration已通過sudo mode並顯示建立表單，但因SEC-F-016與缺少functional HTTPS webhook endpoint而未submit；0 App／credential created。
- 未觀察到可用controller HTTPS webhook endpoint；在endpoint與private Human control成立前不能建立functional sandbox App。

Environment與repository建立是HD-004-05授權的sandbox side effect；沒有production ruleset、formal Approval、App、credential或IAM mapping。SEC-F-016關閉前不得繼續App／ruleset activation。

## Local Verification

2026-07-17執行：

- `python -m unittest discover -s tests -v`：56 tests，全部通過；其中13個為merge authorization contract／security tests。
- `python scripts/validate_sdd.py`：0 errors、0 warnings。
- `python scripts/validate_enterprise.py`：0 errors、0 warnings。
- `python scripts/run_evals.py`：4 cases，0 errors。
- `python scripts/run_agent_evals.py`：4/4 passed。
- runtime audit validation：18 runs，0 errors。
- Kit Manifest：279 files，`--check`通過。
- portability、compileall與`drift_check.py --change CHG-2026-003`通過；0 unspeced drift。

這些是local implementation verification，不是TASK-009 independent Evidence，也不關閉SEC-F-009～015。

## Rollback

本地rollback為停止使用sandbox engine／Adapter並保持Mode B blocked；不得刪除production protection（目前未啟用）、加入bypass或公開IAM mapping。external sandbox若部署，依Runbook revoke App／keys並保留required check造成merge freeze。

## Handoff

下一步需Human選擇升級GitHub plan以取得private Environment protection，或另提具等效private Human control的新Requirement／Design Addendum。SEC-F-016關閉且提供HTTPS webhook endpoint後，才能建立／安裝sandbox GitHub App並保存去識別configuration digest，再交由獨立TASK-009 Security Reviewer／QA。production Mode B、formal Approval merge與TASK-005仍未授權。
