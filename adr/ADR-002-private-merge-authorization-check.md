# ADR-002：Private Merge Authorization with App-Sourced Required Check

- Status：Accepted — Sandbox Implementation Boundary
- Date：2026-07-17
- Decision Owners：Architect、Security Owner、Change Manager
- Related Change：CHG-2026-003
- Related Requirements：REQ-MERGE-AUTHZ-001、SEC-MERGE-PRIVACY-003

## Context

正式 Approval merge 必須由受信任 Human control授權，但公開 Starter Kit 不能公開真實 Change Manager、GitHub Team 或 IAM mapping。公開 CODEOWNERS placeholder沒有 enforcement；在 public repository直接設定具有真實 reviewers 的 protected Environment，則可能透過 Actions／deployment history暴露 reviewer activity。

## Decision Drivers

- ruleset層確實阻擋 direct／unauthorized merge；
- reviewer資格與 IAM mapping不進 public surfaces；
- required check不可被同名 status spoofing；
- authorization精確綁定 PR head、Approval digest與target commit；
- service failure、replay與stale result一律 fail closed；
- public Kit可攜，但 private deployment overlay由導入者持有。

## Options

| Option | Benefits | Costs / Risks |
|---|---|---|
| 公開 CODEOWNERS 真實 Team／user | GitHub原生、簡單 | 公開 IAM關係；與 privacy requirement衝突 |
| public repository protected Environment reviewers | 原生 Human pause | public deployment／review activity可能洩漏身分；仍需將結果連到 merge |
| 一般 PR review＋required CI | 容易部署 | 無法證明 reviewer具 private Change Manager role；同名 status可能被 spoof |
| 全私有 mirror／手工 attestation | 隱私強 | public branch enforcement與exact-head binding容易脫節 |
| private Environment＋GitHub App required check＋public ruleset | private role proof、public exact-head enforcement、可鎖定 check source | 需運營App、private control repo、replay store與跨邊界attestation |

## Decision

採用 hybrid option：private protected Environment執行 Change Manager review與private validation；GitHub App驗證最小attestation後，以唯一 App identity對public exact PR head建立 `approval-merge-authorization` check；public ruleset要求此App來源的strict check與PR reviews，且不配置正式Approval bypass。

GitHub App只負責分類、驗證、attestation correlation與check conclusion，不自動核准Gate、不自動合併、不持有公開IAM mapping。公開 CODEOWNERS保持placeholder，可供Starter Kit示例但不是formal authorization source。

## Consequences

### Positive

- public repository可驗證「有受信任private control授權」，但無須知道真實reviewer。
- App source pinning與exact-head check降低同名status、stale approval與TOCTOU風險。
- private control不可用時ruleset自然阻擋merge，符合Mode B fail closed。

### Negative / Debt

- GitHub App private key、webhook secret、attestation key、private Environment與replay store成為高價值運營資產。
- 需sandbox證明GitHub plan、ruleset、check source與Environment功能實際可用。
- public與private audit需以digest correlation調查，日常操作比單一repository複雜。
- merge queue若啟用，需額外支援merge-group SHA contract。

## Security and Operational Constraints

- App least privilege：Metadata read、Pull requests read、Contents read、Checks write。
- webhook必須驗證SHA-256 HMAC並執行delivery replay protection。
- private Environment啟用required reviewers、prevent self-review、disallow bypass。
- public check不得揭露reviewer／role／private repository metadata。
- rollback是merge freeze並保留required check，不是移除protection或公開mapping。

## Revisit Conditions

- GitHub提供原生private role attestation且能直接作ruleset merge requirement。
- GitHub deployment visibility或organization identity privacy contract有可驗證變更。
- 導入者啟用merge queue、中央IAM decision service或跨repository approval ledger。

## Decision Record

2026-07-17 Human以HD-004-01～05接受本ADR、Mode B implementation L3 controls及role-based credential custody baseline，只授權TASK-008 sandbox implementation。此決策不授權production Mode B、formal Approval merge、TASK-005、residual risk acceptance或任何public IAM mapping。
