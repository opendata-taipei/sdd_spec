# CHG-2026-003 Design Addendum 004 Human Decision Packet

- Status：Accepted — HD-004-01～05
- Date：2026-07-17
- Scope：Requirement Addendum 001、Design Addendum 004、ADR-002、Security Review Addendum 004
- Formal Change State：DRAFT／PROPOSAL；next formal Gate G1
- Mode B：Fail Closed

## Requested Decisions

### HD-004-01 — Risk Classification

**Recommended decision：TASK-008／009 及 Mode B merge authorization implementation 以 L3 執行。**

Rationale：GitHub App具有 `checks:write`，其結果直接控制formal Approval能否通過ruleset；App private key或attestation key遭竊可能偽造authorization（SEC-F-013 Critical）。L3要求的職責分離與獨立Security verification與此風險相稱。

Alternative：維持L2。此選項必須另行記錄為risk classification decision，且不能減少SEC-F-009～015 required controls；Security Review仍可拒絕implementation readiness。

### HD-004-02 — Architecture Decision

**Recommended decision：接受ADR-002的hybrid control plane。**

- public ruleset要求指定GitHub App來源的strict `approval-merge-authorization` check；
- private protected Environment保存真實Change Manager reviewers與IAM mapping；
- App只驗證／回報check，不自動merge、不核准Gate；
- public CODEOWNERS維持placeholder，不作formal role proof；
- service不可用時merge freeze，不允許bypass。

Reject時Mode B繼續blocked，需提出不公開IAM mapping且能提供等效exact-head enforcement的新Design Addendum。

### HD-004-03 — Role Ownership and Separation

**Recommended role contract：**

| Asset／Decision | Accountable Role | Operator／Reviewer | Separation Rule |
|---|---|---|---|
| GitHub App registration／installation | Repository Admin | App Operator | 不得由Approval作者或本次private authorizer單獨變更 |
| App permission與ruleset expected source | Security Owner | Repository Admin | Security Owner review後由Repository Admin套用；QA獨立驗證 |
| private Environment reviewer policy | Change Manager | Repository Admin | Approval作者不得是唯一reviewer；prevent self-review |
| reviewer／IAM mapping | Change Manager | private IAM Operator | 不進public repository；App Operator不得自行授權自己 |
| App private key／webhook secret | Security Owner | private Secret Custodian | Repository content／workflow author不可讀取raw value |
| attestation signing／MAC key | Security Owner | private Control Operator | 與public App installation設定分離；禁止輸出至public logs |
| sandbox security verification | Security Reviewer | QA Lead | 不得由TASK-008主要implementer自行簽核 |
| Mode B activation | Change Manager／Security Owner | Repository Admin | 必須引用TASK-009 Evidence；Agent不得核准 |

此表只指定role contract，不記錄任何真人login、Email、numeric ID、Team name或private repository名稱。實際assignment只存在private deployment overlay／企業IAM。

### HD-004-04 — Credential Custody Baseline

**Recommended provider-neutral baseline：**

1. App private key、webhook secret與attestation key只保存於private secret manager／protected Environment，不保存於Git、public Actions variables、artifact或local shared workspace。
2. App使用短期installation access token；public repository permissions限制為Metadata read、Pull requests read、Contents read、Checks write。
3. webhook與attestation使用不同key；request／response domain separation及versioned canonical payload為mandatory。
4. raw key access最小化並有private audit；credential export、rotation、revocation與emergency disable需雙人review。
5. suspected compromise立即停用App／revoke key並維持required check，使Mode B merge freeze；不得移除ruleset作為復原方式。
6. rotation後所有pending attestation失效，必須對current head重新送private review。
7. retention期限與secret-manager產品由private deployment policy決定，不得寫入public Kit；sandbox前必須有可稽核設定。

### HD-004-05 — Bounded Implementation Authorization

**Recommended authorization：只授權TASK-008 sandbox implementation，不授權production Mode B。**

Allowed：synthetic repository／Change／Approval、private control sandbox、least-privilege App、test ruleset、failure-path與privacy instrumentation。

Not allowed：production default-branch activation、formal Approval merge、TASK-005 remediation、real IAM mapping輸出、Gate／Release approval、ruleset bypass或residual risk acceptance。

TASK-009須由獨立Security Reviewer／QA執行；只有SEC-F-009～015具有可重現Evidence並重新review後，才能另送Mode B activation decision。

## Entry Criteria for TASK-008

- [x] HD-004-01～05有明確Human Decision。
- [x] Requirement Addendum 001、Design Addendum 004、ADR-002與Security Review Addendum 004完成review。
- [ ] private control owner、Secret Custodian、Repository Admin與independent reviewer已在private overlay指派。
- [ ] sandbox repository／App installation範圍與cost／plan可用性已確認。
- [ ] credential rotation／revocation與merge-freeze runbook可供private reviewer檢查。
- [ ] public repository Mode B仍fail closed。

## Exit and Evidence for TASK-008

- App permission與ruleset設定export，不含private identity。
- canonical request／attestation schema與hash fixtures。
- positive flow僅在private review與exact-head validation後成功。
- invalid signature、replay、mixed diff、fork、stale head、self-review、outage、same-name spoof全部failure／pending。
- public PR、check、log、artifact、deployment surface與Kit privacy scan為0 finding。
- TASK-009 independent handoff；不宣稱Mode B完成。

## Proposed Human Decision Wording

> 核准 CHG-2026-003 HD-004-01～05：Mode B implementation風險採L3；接受Requirement Addendum 001、Design Addendum 004與ADR-002的hybrid private merge authorization設計；接受Security Review Addendum 004 required controls及角色／credential custody baseline；只授權TASK-008 sandbox implementation，不授權production Mode B、formal Approval merge或TASK-005。Mode B維持fail closed，待TASK-009獨立驗證與後續Human Decision。

## Non-Decision Notice

本packet本身不是Gate approval、risk acceptance、Security Exception、implementation authorization或身分證明。Agent不得勾選Entry Criteria、建立Approval JSON或把對話內容改寫成OIDC／GitHub formal approval。

## Human Decision Record

2026-07-17 Human明確核准HD-004-01～05：Mode B implementation採L3；接受hybrid private merge authorization、required controls與role／credential custody baseline；只授權TASK-008 sandbox implementation。production Mode B、formal Approval merge、TASK-005與TASK-009 sign-off均未授權。
