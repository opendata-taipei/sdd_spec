# CHG-2026-003 Requirement Addendum 001：Privacy-Preserving Equivalent Merge Control

- Status：Accepted — TASK-008 Sandbox Scope Only
- Date：2026-07-17
- Current Change Risk：L2
- Mode B Implementation Risk：L3（HD-004-01 accepted）
- Affected Requirement：REQ-GATE-WORKFLOW-001 AC-016
- Related Feature：FEAT-002
- Related Decision：ADR-002（Proposed）

## Context

Mode A 已證明 protected Environment workflow 能建立 privacy-preserving Approval artifact；Mode B 仍缺少可證明的 merge enforcement。公開 `CODEOWNERS` 若列出真實 Change Manager 或 Team，會揭露 IAM 關係；只放 placeholder 又不能形成正式授權控制。此 Addendum 定義以 public ruleset、來源鎖定的 required check，以及 private protected Environment reviewers 組成等效控制。

本 Addendum 在核准後只 supersede AC-016 中「必須以公開 CODEOWNERS 表達 Change Manager」的實作假設；Human review、受保護合併、職責分離與不得自動核准 Gate 的原則不變。

## Functional Requirements

### REQ-MERGE-AUTHZ-001

- Statement：WHEN pull request 可能新增正式 Approval record THEN public repository SHALL 只在 exact PR head SHA 具有由指定 GitHub App 產生的成功 `approval-merge-authorization` check，且 ruleset 的所有其他條件均成立時允許合併。
- Priority：Must
- Source：REQ-GATE-WORKFLOW-001 AC-016、SEC-F-006、SEC-F-007
- Acceptance Criteria：
  - AC-021：default branch ruleset 要求 pull request、至少一個非作者 review、dismiss stale approvals、require approval of the most recent reviewable push、strict required checks，並阻擋 branch deletion 與 force push。
  - AC-022：`approval-merge-authorization` 的 expected source 必須鎖定已核准 GitHub App；不得接受同名 commit status、其他 App、使用者 token 或可由一般 write actor 任意建立的 check。
  - AC-023：check 必須綁定當下完整 40 字元 PR head SHA；push、rebase、base update、Approval diff 或 private attestation 改變後，舊結果不得授權新 head。
  - AC-024：正式 Approval path 不得有 repository admin、ruleset actor、workflow 或 Environment bypass；緊急處置只能停止 merge 並走另案 Human Decision，不得降級為公開 mapping 或人工同名 status。

### REQ-APPROVAL-PR-001

- Statement：WHEN required check 分類並驗證 pull request THEN 系統 SHALL 對 Approval PR 套用單一目的、不可混合且可重現的 diff contract。
- Priority：Must
- Source：Approval Schema、Enterprise Policy v1.4
- Acceptance Criteria：
  - AC-025：Approval PR 只能新增一個位於受管 `changes/<change>/approvals/` 的 `.json`；不得修改或刪除既有 Approval，也不得混入 code、workflow、policy、Evidence 或其他檔案。
  - AC-026：新增 record 必須通過 schema、artifact hash、Change／Gate policy、Evidence reference、identity provider、role、separation of duties、duplicate actor 及 commit binding 驗證。
  - AC-027：commit binding 必須指向被核准的 immutable target commit；PR head、target commit、Approval digest 與 private attestation 的關係必須在版本化 contract 中無歧義。
  - AC-028：非 Approval PR 仍須由指定 App 對 exact head 建立成功且明確標記 `not_applicable` 的 check；不得依賴 path-skipped workflow 的成功語意。

### SEC-MERGE-PRIVACY-003

- Statement：WHEN private Change Manager 執行 merge authorization review THEN public repository SHALL NOT 揭露真實 reviewer login、Email、numeric actor ID、Team／role mapping 或 private IAM 結構。
- Priority：Must
- Source：SEC-PRIVACY-002、ADR-001、SEC-F-007
- Acceptance Criteria：
  - AC-029：真實 reviewer allowlist、role mapping、Environment reviewer identity 與授權稽核資料只存在 private control repository／private deployment overlay，不進 public Git、Actions log、check summary、artifact 或 Starter Kit。
  - AC-030：public check output 最多包含 contract version、public repository／PR、head SHA、Change ID、Approval digest 與不含身分資訊的 attestation digest／opaque reference。
  - AC-031：public PR review 可作一般 code review，但不得被當作 private Change Manager 身分證明；正式 merge authorization 必須由 private control plane 產生。
  - AC-032：privacy scan 對 public diff、check output、workflow log、deployment history、artifact 與 package 的真實 login／Email／raw actor ID／mapping finding 必須為 0。

### OPS-MERGE-REL-004

- Statement：WHEN merge authorization 的任一 trust dependency 不可用或無法驗證 THEN control plane SHALL fail closed 且保留可稽核、可重試、不重複授權的結果。
- Priority：Must
- Source：OPS-REL-003、SEC-F-006
- Acceptance Criteria：
  - AC-033：webhook signature 無效、delivery replay、private Environment／mapping／secret 缺失、fork PR、mixed diff、timeout、attestation mismatch、duplicate request 或 GitHub API error 時不得產生成功 authorization。
  - AC-034：controller 必須驗證 `X-Hub-Signature-256`、以 delivery ID 與 request digest 執行 idempotency／replay protection，並以 installation token 的 least privilege 寫入 check。
  - AC-035：private protected Environment 必須啟用 required reviewers、prevent self-review 與 disallow administrator bypass；Environment secret 只在 review 通過後提供給執行 job。
  - AC-036：控制面中斷時 required check 保持 pending／failure；恢復後只能針對仍為 current head 的相同 request 重試，不得沿用 stale authorization。

## Traceability

| Requirement | Design | ADR | Task | Test | Status |
|---|---|---|---|---|---|
| REQ-MERGE-AUTHZ-001 | DES-MERGE-RULESET-001, DES-MERGE-CHECK-001 | ADR-002 | TASK-008, TASK-009 | TEST-MERGE-001, TEST-RULESET-001, TEST-MERGE-FAIL-001 | Proposed |
| REQ-APPROVAL-PR-001 | DES-MERGE-CHECK-001, DES-MERGE-ATTEST-001 | ADR-002 | TASK-008, TASK-009 | TEST-MERGE-001, TEST-MERGE-FAIL-001 | Proposed |
| SEC-MERGE-PRIVACY-003 | DES-PRIVATE-CONTROL-001, DES-MERGE-ATTEST-001 | ADR-001, ADR-002 | TASK-008, TASK-009 | TEST-MERGE-PRIVACY-001 | Proposed |
| OPS-MERGE-REL-004 | DES-MERGE-CHECK-001, DES-PRIVATE-CONTROL-001 | ADR-002 | TASK-008, TASK-009 | TEST-MERGE-FAIL-001, TEST-MERGE-REPLAY-001 | Proposed |

## Assumptions and Open Decisions

- GitHub plan／organization policy 能提供 repository ruleset、expected-source required check 與 private repository protected Environment；必須在 sandbox 實測，不以文件推定為 Evidence。
- GitHub App 的 private key、webhook secret、installation configuration 與 reviewer mapping 由 private operator 管理，不屬於 public Kit。
- TASK-008／009 依 L3 separation 與 security review執行；此決策不改寫CHG主state的既有L2歷史，也不授權production activation。
- Mode B 在 Requirement、Design、ADR、安全複審與 sandbox verification 完成前維持 fail closed。

## Human Decision Record

2026-07-17 Human先核准本Addendum的規劃方向，後以HD-004-01～05接受本Requirement與L3 Mode B implementation controls，並只授權TASK-008 sandbox implementation。這不是formal Gate Approval、production Mode B activation、Security Exception、formal Approval merge或TASK-005授權。
