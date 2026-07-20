# CHG-2026-003 Test Plan

## Entry Criteria

- [x] Requirement／Design及Addendum 005已依各自bounded scope核准
- [x] local synthetic fixtures可用；protected GitHub Environment不可用並記為SEC-F-016，private credential／mapping未放入workspace

## Test Cases

| Test ID | Requirement | Level | Scenario | Expected | Evidence |
|---|---|---|---|---|---|
| TEST-ROLE-001 | REQ-ROLE-MAP-001 | Unit | 合法 protected JSON、allowed roles 與 numeric actor IDs | parse 成 canonical in-memory mapping，不輸出原文 | unittest output |
| TEST-ROLE-002 | REQ-ROLE-MAP-001, SEC-IDENTITY-002 | Security | missing／oversize／invalid JSON、duplicate key、extra property、invalid actor ID、unknown／duplicate role | 全部 fail closed，stdout 無 mapping | unittest output |
| TEST-ROLE-003 | REQ-GATE-RESOLVE-001 | Unit | actor missing、unknown Gate、零個／多個 eligible role 與唯一 role | 只有唯一 eligible role 成功 | unittest output |
| TEST-IDENTITY-001 | REQ-PRIVATE-ACTOR-001 | Unit | 相同／不同 repo、actor、pepper 的 HMAC fixtures | deterministic、domain-separated、full digest pseudonym | unittest output |
| TEST-IDENTITY-002 | REQ-PRIVATE-ACTOR-001, SEC-IDENTITY-002 | Security | missing／non-canonical Base64／非 32-byte pepper、invalid actor／repo，以及禁止 raw hash fallback | 全部 fail closed；無 raw identifier | security test report |
| TEST-WORKFLOW-001 | REQ-GATE-WORKFLOW-001 | Integration | protected Environment、合法 OIDC、mapping、pepper、Evidence 與 commit | 只產生單一 schema-valid Approval artifact | GitHub Actions artifact／run URL |
| TEST-WORKFLOW-002 | REQ-GATE-WORKFLOW-001, OPS-REL-003 | Failure | mapping／pepper／OIDC／Evidence 缺失、shell metacharacter input、job cancellation、existing target | 非 0、cleanup 完成、不覆寫、無 partial Approval artifact | Actions negative test log |
| TEST-SECURITY-001 | SEC-IDENTITY-002 | Security | spoofed actor／repository／audience／workflow ref、expired token、role/input injection、invalid actor reference／claim mismatch | 全部拒絕，0 unauthorized Approval | security test report |
| TEST-PRIVACY-001 | SEC-PRIVACY-002 | Privacy | 掃描 Git diff、package、stdout／stderr、workflow log 與 artifact | 0 login／Email／raw actor ID／mapping／pepper／JWT／Token finding | privacy scan report |
| TEST-KIT-PRIVACY-001 | SEC-PRIVACY-002, OPS-REL-003 | Security regression | fixture 與實際 workspace 存在 top-level `tmp/` raw logs | build／`--check` 均排除所有 `tmp/` descendants；check 唯讀；其他 unmanaged public file 仍 fail closed | unittest output／Kit Manifest／package round-trip |
| TEST-PERF-001 | NFR-PERF-003 | Performance | 32 KiB mapping fixture 重複 100 次 | p95 < 200 ms；process peak RSS < 64 MiB | benchmark report |
| TEST-REMEDIATION-001 | REQ-STATE-REMEDIATION-001, OPS-REL-003 | Integration | CHG-2026-003 bootstrap 與 CHG-2026-002 正式 G1～G4 Approval 合併後順序 transition | 每 Gate fail closed；event chain append-only、current timestamp、remediation reason、state projection 與 Enterprise validation通過 | repository events／CI log |
| TEST-MERGE-001 | REQ-MERGE-AUTHZ-001, REQ-APPROVAL-PR-001 | Sandbox integration | 單一合法Approval新增、private Change Manager review、valid attestation與exact current head | 指定App check success；Human merge可用；App不自動merge | sandbox PR／check／private attestation digest |
| TEST-MERGE-FAIL-001 | REQ-MERGE-AUTHZ-001, REQ-APPROVAL-PR-001, OPS-MERGE-REL-004 | Security failure | fork、mixed diff、modify/delete existing Approval、invalid schema/hash/policy/evidence/role、self approval、head/base/target change、private rejection/cancel/timeout | 每案pending或failure；0 unauthorized success／merge | sandbox negative matrix |
| TEST-MERGE-REPLAY-001 | OPS-MERGE-REL-004 | Security | invalid webhook HMAC、duplicate delivery、replay nonce、expired attestation、API retry與service outage | constant-time signature validation、idempotent result、stale/replay rejected、outage fail closed | controller test／private audit digest |
| TEST-RULESET-001 | REQ-MERGE-AUTHZ-001 | Platform security | direct／force push、stale review、同名status由非指定source建立、App check缺少、ruleset bypass檢查 | default branch全部blocked；只有指定App current-head check可滿足condition | ruleset API export／sandbox attempts |
| TEST-MERGE-PRIVACY-001 | SEC-MERGE-PRIVACY-003 | Privacy | 掃描public PR、review、check、Actions／deployment、artifact、Git diff與Kit package | 0真實login／Email／numeric ID／Team／role mapping／private repository metadata finding | privacy scan report |
| TEST-DEVICE-AUTH-001 | REQ-DEVICE-AUTH-001 | Sandbox integration | fresh device flow、numeric identity、unique private role與current Approval request | approved attestation v2；token erased；App exact-head check success | private run digest／public check |
| TEST-DEVICE-SEPARATION-001 | REQ-DEVICE-AUTH-001 | Security | reviewer等於PR author／Approval actor、unknown／ambiguous role、denied／expired／substituted session | 全部failure；0 success check | private negative matrix |
| TEST-POLL-001 | OPS-POLL-AUTHZ-005 | Integration | open PR polling、non-Approval與Approval classification、bounded retry | explicit not_applicable或pending auth；no skipped success | poll audit digest |
| TEST-POLL-STALE-001 | OPS-POLL-AUTHZ-005 | Security | device flow期間head／base／policy／installation改變 | stale request invalid；需要new device flow | sandbox runs |
| TEST-CONTROLLER-CUSTODY-001 | SEC-CONTROLLER-CUSTODY-004 | Security | host、service account、secret store、artifact/config digest、rotation/revocation review | L3 custody controls pass；任一缺失fail closed | private host review digest |
| TEST-DEVICE-PRIVACY-001 | SEC-CONTROLLER-CUSTODY-004, SEC-MERGE-PRIVACY-003 | Privacy | public／private logs、process args、crash/audit artifacts掃描 | 0 device code／token／raw ID／mapping／key finding on public surfaces | privacy report |

## Exit Criteria

- [ ] 所有 Must Requirement 已通過
- [ ] 無未接受的 Critical／High Defect
- [ ] 測試證據已保存

## Implementation Verification Status

| Scope | Status | Notes |
|---|---|---|
| TEST-ROLE-001～003 | Pass | strict parser、failure paths、unique policy role 與 stdout contract |
| TEST-IDENTITY-001～002 | Pass | HMAC domain separation、canonical pepper、numeric IDs、exact reduced claim |
| TEST-WORKFLOW-001 | Pass | local synthetic end-to-end pass；protected Environment success run `29354763421` 的 schema-valid single artifact、context binding 與 raw-log privacy scan 已驗證；artifact 未合併且不構成正式 Approval |
| TEST-WORKFLOW-002 | Pass for Addendum 002 scope | local missing／malicious／existing-target paths pass；unknown-Gate run `29388919217` fail closed；run `29407591960` attempt 3 在 pip 階段取消，identity／Approval／upload skipped、always cleanup success、0 current artifact；OIDC-file post-creation hard cancellation仍依 ephemeral runner boundary |
| TEST-SECURITY-001 | Pass locally | issuer／audience／repository／actor／workflow_ref／run／time／claim mismatch 拒絕 |
| TEST-PRIVACY-001 | Pass for Addendum 002 scope | success run `29354763421`、negative run `29388919217` 與 cancellation run `29407591960` attempt 3 raw logs／artifact contract 均已掃描，0 login／Email／raw actor ID／mapping／pepper／JWT／Token finding |
| TEST-KIT-PRIVACY-001 | Pass | exact top-level `tmp/` exclusion、nested runtime fixture、read-only `--check`、current workspace 與 local package round-trip 均通過；Quality Gates run `29402752423` 的 Windows／Linux jobs 與 checksum comparison 成功 |
| TEST-PERF-001 | Pass | 32 KiB fixture ×100，p95 與 peak RSS assertions 通過 |
| TEST-REMEDIATION-001 | Partial | reducer reason projection pass；正式 merged Approvals 與 CHG-2026-002 pilot 尚待 TASK-005 |
| TEST-MERGE-001 | Partial — local pass | request／attestation schemas、single Approval、exact head/base/target/policy與public output synthetic flow通過；GitHub App／private Environment platform run待external sandbox |
| TEST-MERGE-FAIL-001 | Partial — local pass | mixed／modified／unsafe Approval、digest mismatch、denied／failed／expired／stale policy paths通過；fork／platform rejection／timeout待external sandbox |
| TEST-MERGE-REPLAY-001 | Partial — local pass | webhook SHA-256 HMAC、atomic delivery idempotency與mismatch rejection通過；deployed endpoint／service outage待external sandbox |
| TEST-RULESET-001 | Planned | 目前ruleset audit為0；正式enforcement尚不存在 |
| TEST-MERGE-PRIVACY-001 | Partial — local pass | public output exact allowlist、private workflow／reviewer marker absence與sandbox placeholder contract通過；GitHub public surfaces scan待external sandbox |
| TEST-DEVICE-AUTH-001 | Partial — local synthetic pass | numeric identity、unique private Change Manager、attestation v2 schema與exact-head public check通過；真實GitHub device OAuth／App待dedicated host |
| TEST-DEVICE-SEPARATION-001 | Partial — local synthetic pass | PR author／Approval actor、unknown／missing／incompatible role與device session reuse均拒絕；TASK-011 independent run未授權 |
| TEST-POLL-001 | Partial — local synthetic pass | bounded public policy、Approval contract與explicit non-Approval classification已有回歸；真實API polling／rate limit未執行 |
| TEST-POLL-STALE-001 | Partial — local synthetic pass | head／base／policy／installation／controller artifact／config／App digest或expiry變更均fail closed；platform run待TASK-011 |
| TEST-CONTROLLER-CUSTODY-001 | Blocked externally | dedicated managed host、service account、secret store與role custody尚未提供；目前workstation不合格 |
| TEST-DEVICE-PRIVACY-001 | Partial — local synthetic pass | public attestation/check allowlist不含numeric ID、mapping、role、device code或token；private host/process/crash scan待TASK-011 |

External sandbox note：2026-07-17已建立private repository與`sdd-merge-authorization` Environment，但GitHub UI不提供required reviewers／prevent self-review，故SEC-F-016阻擋TEST-MERGE-001 platform positive path與TASK-009；未建立App、ruleset、secret或formal Approval。

Addendum 005 note：2026-07-17 Human只授權TASK-010 synthetic sandbox。SEC-F-013、016～022保持Open；未建立webhook-inactive App、未產生或下載private key、未執行真實device flow，production Mode B、formal Approval merge、TASK-005與TASK-011 sign-off均未授權。

Cross-platform Quality Gates run `29351982743` 已通過 Linux／Windows package round-trip 與 checksum comparison；此結果不改變 protected Environment tests 的 Partial 狀態。
