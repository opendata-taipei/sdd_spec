# CHG-2026-003 Design Addendum 005：Device-Flow Private Authorizer and Polling Check

- Status：Accepted for TASK-010 synthetic sandbox only — 2026-07-17 Human Decision
- Date：2026-07-17
- Risk：L3
- Requirements：REQ-DEVICE-AUTH-001、OPS-POLL-AUTHZ-005、SEC-CONTROLLER-CUSTODY-004
- ADR：ADR-003（Accepted for TASK-010 synthetic sandbox only）
- Finding：SEC-F-016
- Tasks：TASK-010／011

## Decision Summary

在不升級GitHub plan的sandbox alternative中，private control不再依賴GitHub Environment／private branch protection。GitHub App webhook保持inactive；一個private managed controller定期poll public PR。遇到Approval PR時，Human authorizer在controller發起的GitHub App device flow完成一次性登入，controller fresh-read numeric identity、private role map及separation conditions，再簽發attestation並以App installation token寫exact-head check。

本設計不使用已建立但unprotected的private repository作權威code、policy、secret或approval store。該repository保持empty／quarantined，直到另有核准用途。

## Architecture

```text
Public PR + public ruleset
        ^                           private boundary
        | App check                        |
GitHub Checks API <--- installation token  |
        ^                                  |
        |                           Managed controller
        |                           - poll current PR
        |                           - private mapping
        |                           - keys / replay audit
        |                                  ^
        |                                  |
        +--------------------------- GitHub App device flow
                                           ^
                                           |
                                    Human authorizer
```

### DES-POLL-CHECK-001

- GitHub App webhook設為inactive，不訂閱events，不需要callback／webhook endpoint。
- controller以bounded interval列出open PR並fresh-readhead、base、files、Approval bytes、policy與check state。
- non-Approval PR寫`not_applicable` success；Approval PR先寫in-progress，再等待explicit Human authorization。
- polling request key為repository ID／PR／head SHA／request digest；同一request idempotent，head或policy改變即invalid。
- App installation限制explicit sandbox repositories；check name與source pinning沿用DES-MERGE-RULESET-001。

### DES-DEVICE-HUMAN-001

1. controller只為current Approval request向GitHub device authorization endpoint取得device／user code。
2. Human只在自己開啟的trusted GitHub device page輸入code；controller不得以email、chat或public log傳送code。
3. controller bounded poll token endpoint，取得expiring user access token後立即呼叫`GET /user`，不接受login作主鍵。
4. numeric ID須在private role map中恰有唯一eligible Change Manager role。
5. controller計算reviewer repository pseudonym，與Approval actor pseudonym及public PR author ID執行separation；不一致才能繼續。
6. user token清除後產生private audit record；attestation不包含raw identity。

device flow user token只證明Human GitHub identity；寫check使用separate App installation token。device authorization denial、timeout、token substitution、identity API failure或role ambiguity全部fail closed。

`change_manager`在此為private merge-authorization policy中的營運角色，不是
`config/enterprise-policy.json.allowed_roles`的G1～G7正式Approval角色。此namespace
分離不得用來新增Gate權限，也不得把Change Manager映射成Security Owner、Release
Manager或其他正式approver。private policy須拒絕Change Manager同時持有App Operator、
Secret Custodian或TASK-011 Security Reviewer職責。

### DES-PRIVATE-HOST-001

controller不得在public Actions、unprotected private repository workflow或shared developer shell執行。sandbox host至少需要：

- dedicated service account、encrypted storage、patched OS、restricted interactive access；
- OS／hardware-backed secret store保存App private key、attestation key、private mapping pepper；
- immutable release digest或signed package、allowlisted outbound GitHub endpoints；
- private append-only／tamper-evident audit，public只保存digest；
- operator／authorizer／independent reviewer分離；
- rotation、revocation、host isolation及merge-freeze runbook。

controller compromise或App key compromise仍可偽造check，因此SEC-F-013／017保持Critical，不能只靠device flow降級。

## Contract Changes

`merge-authz-request/v1`維持相容。private attestation下一版建議`merge-authz-attestation/v2`新增：

- `trigger_mode=poll-device-flow`
- controller artifact／configuration digest
- App ID／installation scope digest
- private identity decision digest（非identity）
- device authorization session digest／expiry（不含device code或token）

public check output維持v1 allowlist，不新增reviewer、host、private repository或device-flow metadata。

## Failure-Closed Matrix

| Condition | Outcome |
|---|---|
| poller down／rate limited／API timeout | missing／pending／failure check；merge blocked |
| unsolicited／reused device code | reject；new session required |
| user token expired／denied／identity mismatch | reject and erase token |
| reviewer not mapped／ambiguous／same as author or Approval actor | failure check |
| controller digest／config／App installation changed | old request and attestation invalid |
| head／base／policy changed during device flow | stale; new request and new Human authorization |
| private audit unavailable | reject; no check success |
| App or controller key suspected compromised | revoke／disable App; ruleset keeps merge frozen |

## Migration and Rollback

Migration只在synthetic sandbox：建立private managed host、註冊webhook-inactive App、選定sandbox installation、先不配置public production ruleset，以manual poll驗證後再交TASK-011。已建立的unprotected private repository不得存secret或作Human Gate。

Rollback為停止controller、disable／uninstall App並保持public required check未啟用或fail closed。不得改回unprotected Environment、public IAM mapping或manual same-name status。

## External References

- GitHub App device flow：<https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-user-access-token-for-a-github-app>
- GitHub App CLI device-flow guidance：<https://docs.github.com/en/apps/creating-github-apps/writing-code-for-a-github-app/building-a-cli-with-a-github-app>
- installation token scope／expiry：<https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app>
- webhook deactivation：<https://docs.github.com/en/apps/maintaining-github-apps/modifying-a-github-app-registration>
- private repository protection plan availability：<https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches>

## Human Decision

Human於2026-07-17接受private managed controller與per-decision GitHub device flow作為AC-035的privacy-preserving equivalent，只授權TASK-010 synthetic sandbox。production Mode B、formal Approval merge、TASK-005與TASK-011 sign-off仍需後續決策。
