# ADR-003：Polling GitHub App with Per-Decision Device Authorization

- Status：Accepted for TASK-010 synthetic sandbox only
- Date：2026-07-17
- Related Change：CHG-2026-003
- Supersedes：ADR-002 private Environment path only if accepted

## Context

SEC-F-016證明目前GitHub plan無法在private repository使用Environment reviewers、protected branches或rulesets。public Environment會洩漏reviewer activity，unprotected private workflow又不能滿足L3 separation，因此需要升級plan或移出GitHub repository control plane。

## Options

| Option | Benefits | Risks／Cost |
|---|---|---|
| 升級GitHub Team／Enterprise | 原生private protection、最接近ADR-002 | recurring cost與organization billing decision |
| unprotected private workflow | 無新增infra | workflow／secret可被未受保護修改；拒絕 |
| public Environment reviewers | 原生review | public identity leakage；拒絕 |
| external IdP approval service | enterprise-grade | 尚無provider／owner／endpoint |
| private managed poller＋GitHub App device flow | 無webhook endpoint、逐次GitHub identity、IAM不公開 | trusted host與App key成Critical資產；需運營poller |

## Decision

TASK-010 sandbox採private managed poller＋per-decision device flow；GitHub App webhook inactive。device user token只驗證Human identity，installation token只寫App check。controller以private numeric mapping、pseudonym與PR author執行separation，public只看到App-sourced exact-head check。

本選項不是對SEC-F-013／017的risk acceptance。若無法提供dedicated host、secret custody與operator／authorizer separation，應回到GitHub plan升級，不得使用一般developer workstation或unprotected Actions workflow。

2026-07-17 Human Decision只授權TASK-010 synthetic sandbox；不授權production Mode B、formal Approval merge、TASK-005或TASK-011 sign-off。SEC-F-013、016～022保持Open。

## Consequences

- Positive：不需要public reviewer、private Environment protection或webhook endpoint；GitHub identity可逐次驗證。
- Negative：poll latency、managed host運維、device-flow phishing與App key compromise風險增加。
- Debt：需要attestation v2、device-flow client、poller state、host hardening與independent security tests。

## Revisit Conditions

- organization升級至支援private protection的GitHub plan。
- 可用enterprise IdP／HSM approval service。
- GitHub提供private reviewer attestation直接供public ruleset使用。
