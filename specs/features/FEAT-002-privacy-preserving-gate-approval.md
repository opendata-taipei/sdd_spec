# FEAT-002：Privacy-Preserving Gate Approval

- Status：Implemented — Mode A Verified；Mode B Blocked
- Owner：Justin
- Target Release：v1.5.0
- Primary Change：CHG-2026-003

## Problem

公開 Starter Kit 不得提交真實 GitHub login 或 actor／role mapping，但正式 Gate Approval 又必須由可信 identity provider、合法 role 與實際 commit SHA 建立。現有 placeholder-only repository 因此無法直接完成正式 Gate lifecycle。

## User Value

導入者可以把真實授權映射保留在 GitHub protected Environment、企業 IAM 或等效的私有控制面；公開 repository 仍可提供完整、可驗證且 fail-closed 的 Approval workflow。

## In Scope

- 受保護 runtime role-map contract 與 strict validation。
- GitHub OIDC reduced claims、commit binding 與唯一 eligible role。
- 缺少／錯誤／衝突 mapping 的 failure-path tests。
- 防止 role map、token、JWT 與不必要身分資料進入 log、artifact、Git 或 Starter Kit package。
- CHG-2026-002 Gate／Event State remediation pilot。
- privacy-preserving equivalent merge control的Requirement／Design／Security規劃，以及後續sandbox驗證。

## Out of Scope

- 公開真實 IAM mapping 或企業組織結構。
- 自動授與 GitHub Team／Environment／CODEOWNERS 權限。
- 在公開repository揭露真實Change Manager reviewers、Team membership或IAM mapping。
- 自動批准 Gate、合併 PR、發布 production 或接受 residual risk。
- 取代企業 IdP、GitHub branch protection 或審計平台。

## Acceptance Outcomes

1. 公開 `config/github-role-map.json` 保持 placeholder，且 package 不含真實 login／Email／Token。
2. 受保護 mapping 可讓合格 actor 產生 schema-valid、OIDC-trusted、commit-bound Approval artifact。
3. mapping 缺失、JSON/schema 錯誤、actor 未授權、role 不合 Gate 或多重 role 時 workflow 非 0 結束且不產生 Approval。
4. workflow log 與 artifact 不包含原始 mapping、OIDC JWT 或 Access Token。
5. CHG-2026-002 可在正式 Approval 合併後，以 append-only events 推進至與實際工作相符的合法狀態。
6. Mode B只有在public ruleset要求指定GitHub App的exact-head check，且Human authorization由private protected Environment或Addendum 005核准的per-decision device-flow private authorizer完成後，才允許Human合併formal Approval；控制面不可用時fail closed。

## Security and Privacy Boundaries

- Role map 是敏感授權中繼資料，即使 GitHub login 本身不是 secret，仍不得放入公開 Kit。
- 授權主鍵使用可信 OIDC numeric actor ID；公開 Approval 只保存由受保護 32-byte pepper 產生的 repository-scoped HMAC pseudonym。
- Runtime mapping 僅在 role-resolution step 最小範圍可見，不得寫入 `$GITHUB_OUTPUT`、artifact 或 diagnostic dump。
- Repository 只保存 contract、placeholder、縮減 OIDC claims 與 Approval record；不保存原始 token。
- 缺少可信 configuration 時沒有 public-map fallback，避免誤用 placeholder 或降級授權。
- formal merge authorization的真實reviewer與IAM mapping只存在private control repository／overlay；public repository只接收無身分資訊、綁定exact head的App check結果。

## Related Changes

| Change | Purpose | Status |
|---|---|---|
| CHG-2026-003 | 建立受保護 role injection、tests 與 CHG-2026-002 remediation pilot | Mode A Verified；Mode B／remediation blocked |

## Dependencies

- Enterprise policy v1.4、Approval／Evidence schemas 與 GitHub OIDC workflow。
- GitHub protected Environment `sdd-approval` 及由 Human administrator 維護的 private mapping。
- 本地 synthetic fixtures 與 protected Environment success／unknown-Gate／cancellation Evidence 已完成；Mode B merge controls與正式 remediation pilot尚待執行。
- Requirement Addendum 001、Design Addendum 004、ADR-002與Security Review Addendum 004 required controls已由HD-004-01～05接受；TASK-008只獲sandbox implementation授權，仍需TASK-009獨立驗證。
- Requirement Addendum 002、Design Addendum 005、ADR-003與Security Review Addendum 005 required controls已接受；TASK-010只完成provider-neutral synthetic contract，dedicated host／App external path與TASK-011獨立驗證未完成。

## Risks

| Risk | Mitigation |
|---|---|
| Secret 出現在 log | 不 echo mapping、最小 step env、log／artifact inspection |
| Role confusion／privilege escalation | strict schema、Gate allowlist、唯一 eligible role、fail closed |
| Environment 未設定造成阻塞 | preflight error 與部署 runbook，不提供公開 fallback |
| 把 Approval artifact 當成已合併 | Enterprise validator 只信任 repository 內經 review 合併的 record |
| required check被同名status spoof或套用stale head | ruleset鎖定expected GitHub App、strict exact-head check、push後重新驗證 |
| public reviewer設定洩漏IAM關係 | reviewers與mapping留在private control repository；public surface只保留最小digest |
| App／private control outage | required check維持pending／failure並freeze merge；不提供bypass |
| GitHub plan不支援private Environment reviewers | SEC-F-016；Mode B fail closed，升級plan或另提等效private control設計 |
| device-flow alternative把信任移到private host | Addendum 005已接受且只授權TASK-010 synthetic sandbox；dedicated host、L3 custody與TASK-011 independent review仍未完成，Mode B fail closed |

## Release History

| Version | Status | Change | Notes |
|---|---|---|---|
| v1.5.0 | Planned | CHG-2026-003 | Initial protected role injection capability |
