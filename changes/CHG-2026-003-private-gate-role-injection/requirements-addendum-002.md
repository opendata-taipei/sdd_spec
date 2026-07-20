# CHG-2026-003 Requirement Addendum 002：Headless Private Authorizer Alternative

- Status：Accepted for TASK-010 synthetic sandbox only — 2026-07-17 Human Decision
- Date：2026-07-17
- Mode B Implementation Risk：L3
- Trigger：SEC-F-016
- Affected Requirements：OPS-MERGE-REL-004 AC-034／035
- Related Design：Design Addendum 005（Accepted for TASK-010 synthetic sandbox only）
- Related ADR：ADR-003（Accepted for TASK-010 synthetic sandbox only）

## Context

實際private sandbox證明目前GitHub plan不提供private Environment required reviewers、prevent self-review、protected branches或rulesets。升級plan以外的候選方案，是把private Human authorization移到受管headless controller：controller以GitHub App device flow對每一次decision重新驗證Human，再以private role map與separation policy判斷；public merge enforcement仍由App-sourced required check與public ruleset提供。

本Addendum若獲接受，僅對此alternative supersede AC-034的「webhook為mandatory trigger」及AC-035的「private protected Environment為mandatory Human Gate」。HMAC、exact-head、no bypass、private IAM、App source pinning及fail-closed要求不變。

## Requirements

### REQ-DEVICE-AUTH-001

- Statement：WHEN private authorizer對Approval PR作出decision THEN controller SHALL要求一次新的GitHub App device-flow user authorization，fresh-read numeric user identity，並只允許private mapping中唯一eligible Change Manager完成decision。
- Priority：Must
- Acceptance Criteria：
  - AC-037：每次decision使用新的device code與短期user access token；不得保存或重用refresh token，token在identity lookup後立即清除。
  - AC-038：controller以authenticated `/user` numeric ID作授權主鍵，不接受login、Email、CLI input或public PR review作role proof。
  - AC-039：private mapping、reviewer identity、device code、user token與authorization audit不進public repository、check output、log、artifact或Kit。
  - AC-040：reviewer numeric ID不得等於public PR author；其repository-scoped pseudonym不得等於Approval actor；App Operator不得以未經device authorization的manual flag產生success。

### OPS-POLL-AUTHZ-005

- Statement：WHEN GitHub App webhook停用 THEN managed controller SHALL以bounded polling或explicit sandbox invocation發現current PR，並只對fresh exact head/base/policy產生check。
- Priority：Must
- Acceptance Criteria：
  - AC-041：poll interval、API timeout、retry與rate-limit backoff有界；controller unavailable時required check保持missing／pending／failure，不得optimistic success。
  - AC-042：每次poll重新取得PR state、diff、Approval bytes、policy與existing checks；request digest／nonce提供idempotency及replay rejection。
  - AC-043：new push、base change、policy change、authorization expiry或App installation change使舊decision失效。
  - AC-044：non-Approval PR由controller明確產生`not_applicable` success；不得依賴skipped workflow。

### SEC-CONTROLLER-CUSTODY-004

- Statement：WHEN controller持有App private key、attestation key與private mapping THEN operator SHALL以L3 custody、host integrity及separation controls保護這些assets。
- Priority：Must
- Acceptance Criteria：
  - AC-045：controller執行於private、專用、patched、encrypted host／service account；keys只在OS／hardware-backed secret store，repository與process diagnostics不可讀出raw value。
  - AC-046：App installation token限制到explicit public sandbox repository及Metadata read、Pull requests read、Contents read、Checks write；token最長一小時且不落disk。
  - AC-047：App Operator、private authorizer與TASK-011 Security Reviewer必須分離；credential access、decision、check write、rotation及revocation保存private tamper-evident audit digest。
  - AC-048：controller binary／source digest、configuration digest、policy digest與App ID需進private attestation；任一不符或host integrity不明時fail closed。

## Traceability

| Requirement | Design | ADR | Task | Test | Status |
|---|---|---|---|---|---|
| REQ-DEVICE-AUTH-001 | DES-DEVICE-HUMAN-001 | ADR-003 | TASK-010 | TEST-DEVICE-AUTH-001, TEST-DEVICE-SEPARATION-001 | Accepted — sandbox only |
| OPS-POLL-AUTHZ-005 | DES-POLL-CHECK-001 | ADR-003 | TASK-010 | TEST-POLL-001, TEST-POLL-STALE-001 | Accepted — sandbox only |
| SEC-CONTROLLER-CUSTODY-004 | DES-PRIVATE-HOST-001 | ADR-003 | TASK-010, TASK-011 | TEST-CONTROLLER-CUSTODY-001, TEST-DEVICE-PRIVACY-001 | Accepted control; external custody unverified |

## Human Decision Required

Human於2026-07-17接受本alternative及required controls，且只授權TASK-010 synthetic sandbox。這不是risk acceptance；SEC-F-013、016～022保持Open，TASK-011、production Mode B、formal Approval merge及TASK-005未獲授權，Mode B維持fail closed。
