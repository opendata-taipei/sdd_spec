# CHG-2026-003 Design Addendum 004：Private Merge Authorization Control Plane

- Status：Accepted — TASK-008 Sandbox Scope Only
- Date：2026-07-17
- Current Change Risk：L2
- Mode B Implementation Risk：L3（HD-004-01 accepted）
- Requirements：REQ-MERGE-AUTHZ-001、REQ-APPROVAL-PR-001、SEC-MERGE-PRIVACY-003、OPS-MERGE-REL-004
- ADR：ADR-002（Accepted — Sandbox Implementation Boundary）
- Tasks：TASK-008、TASK-009

## Decision Summary

Mode B 採用 hybrid control plane：public repository ruleset 永久要求指定 GitHub App 的 `approval-merge-authorization` check；App 對非 Approval PR 回報明確 `not_applicable`，對 Approval PR 則等待 private control repository 的 protected Environment review 與 deterministic validation，再對 exact public PR head SHA 回報結果。真實 reviewer 與 IAM mapping 全程留在 private control plane。

public repository 不部署具有真實 reviewers 的 Environment，因 public repository 的 deployment／Actions surfaces 可能暴露 reviewer activity；公開 `CODEOWNERS` 保持 placeholder，不能作為正式角色證明。

## Architecture

```text
Public PR / exact head SHA
        |
        v
GitHub App webhook controller ---- reject ----> failed required check
        |
        | Approval PR: normalized request digest
        v
Private control repository
  protected Environment
  private Change Manager reviewers
  prevent self-review / no bypass
        |
        v
Private deterministic validator
        |
        | signed/digested minimal attestation
        v
GitHub App Checks API
  approval-merge-authorization @ exact head SHA
        |
        v
Public ruleset permits or blocks merge
```

### DES-MERGE-RULESET-001 — Public Enforcement

default branch ruleset SHALL：

1. require pull request、至少一個非作者 review、dismiss stale reviews、require approval of the most recent reviewable push；
2. require strict `approval-merge-authorization`，expected source 鎖定核准的 GitHub App；
3. block direct push、force push 與 branch deletion，正式 Approval path 不配置 bypass actor；
4. 保留一般 CI required checks；merge queue 若啟用，App 必須另支援對 merge-group SHA 評估，否則 Mode B 不得宣告相容。

ruleset 的有效設定必須由 GitHub API／UI export、direct-push negative test 與 stale-check negative test共同證明，不能只以 repository 設定文件或 401 response 推定。

### DES-MERGE-CHECK-001 — GitHub App Check Producer

GitHub App 是同名 required check 的唯一合法 producer。最小 repository permissions 為 Metadata read、Pull requests read、Contents read、Checks write；不得要求 Contents write、Administration write 或公開 IAM read。App 使用 installation access token，接收 `pull_request`／必要的 merge-group lifecycle events。

controller 對每個 current head 建立 check run：

- 非 Approval PR：完成結論 `success`，summary 明確為 `not_applicable`；不得用 path-filter skipped job。
- Approval PR：先標記 in progress，再等待 private authorization；只有 contract、policy、diff 與 attestation 全部有效才 `success`。
- 無效／拒絕／逾時：`failure`；外部服務暫時不可用可維持 queued／in progress，但不得成功。
- 新 push：建立新 head check；舊 head check 不得轉移或重用。

Approval PR classifier 只接受單一新增 `changes/<change>/approvals/*.json`。任何 rename、modify、delete、symlink、submodule、mixed file、path traversal、oversize 或 ambiguous diff 都 fail closed。validator 驗證 Approval schema、hash、Change／Gate policy、Evidence、role、identity provider、actor uniqueness、separation of duties與 target commit binding。

### DES-PRIVATE-CONTROL-001 — Private Human Authorization

private control repository／deployment overlay 保存：

- protected Environment `sdd-merge-authorization`；
- 真實 Change Manager reviewer membership 與 IAM mapping；
- webhook secret、GitHub App private key reference、attestation signing／HMAC key及 replay store；
- private request／review／decision audit log。

Environment 必須 required reviewers、prevent self-review、disallow bypass。public PR 作者、Approval actor、private authorizer 與 App operator 的 separation 規則依 enterprise policy 驗證；無法解析任何一方時拒絕。Environment secret 只在 reviewer 放行後提供，拒絕或取消不得產生成功 attestation。

### DES-MERGE-ATTEST-001 — Cross-Boundary Contract

version `merge-authz-attestation/v1` 的 canonical request 至少綁定：public repository numeric ID、PR number、full head SHA、base ref／base SHA、Change ID、Approval path、Approval SHA-256、target commit、policy digest、request nonce 與 expiration。private decision 加入 decision、private control workflow identity、review policy result 與完整 request digest後簽章／MAC。

public check summary 僅可揭露 contract version、public repository／PR、head SHA、Change ID、Approval digest 與 attestation digest或無身分資訊的 opaque reference。不得包含 reviewer login、Email、numeric ID、Team name、role mapping、private repository URL／name或 secret-derived authorization material。

attestation 是 App 決定 check conclusion 的輸入，不作為 public Approval actor identity，也不得取代 Approval schema、OIDC identity 或 Human Gate。

## Sequence and State Rules

1. PR opened／synchronized 時 App 以 webhook HMAC 驗證 delivery，正規化 public request並記錄 delivery ID。
2. App 重新讀取 GitHub API 的 current PR head／diff，不信任 webhook payload 作唯一來源。
3. 非 Approval PR 產生 exact-head `not_applicable` success；Approval PR 建立 pending check並送入 private control。
4. private Environment 完成 Human review後 validator 重新驗證 request、policy、expiry與 separation，產生最小 attestation。
5. App 再次查詢 current head；只有 head／digest 未變且 attestation 有效才將該 head check設為 success。
6. ruleset 在所有 review／CI／required check 均成功時才允許 Human merge。App 不呼叫 merge API。

## Failure-Closed Matrix

| Condition | Required Outcome |
|---|---|
| webhook signature invalid／delivery replay | 拒絕處理；無 success check；private audit記錄去識別事件 |
| fork PR／mixed diff／existing Approval modified | failure check |
| private Environment rejected／cancelled／bypassed／unavailable | failure或pending；不得 success |
| mapping、App key、attestation key或policy digest missing | failure；無 public fallback |
| PR head、base、target commit或Approval digest changed | stale request invalidated；新 head重新評估 |
| duplicate delivery／retry | idempotent return；不得建立第二個 authorization |
| GitHub API timeout／rate limit | bounded retry後 pending／failure；不得 optimistic success |
| public output privacy finding | failure；停止 Mode B verification並啟動 security incident procedure |

## Operations, Migration, and Rollback

Migration waves：

1. 先在 sandbox private control repository 安裝 least-privilege App、設定 protected Environment與 synthetic reviewers。
2. 以非 default test branch／test repository驗證 positive、negative、privacy、replay、stale head、direct push、App source pinning及 service outage。
3. Security re-review確認 findings closed後，Human 才能決定 L3、Addendum／ADR approval與 production ruleset activation。
4. activation 後先觀察 fail-closed check，不合併正式 Approval；證據完整後才另行授權 Mode B pilot。

Rollback 是停用 Mode B Approval merge並保持 required check阻擋，不是移除 ruleset或改用 public CODEOWNERS。若 App 必須停機，ruleset持續要求 check，Change Manager 宣告 merge freeze；修復後以新 head／新 request重新驗證。任何 temporary bypass 都超出本 Addendum，需獨立 Critical Change與 Human Decision。

## Verification Evidence

- ruleset JSON／API export 與 exact App source ID；
- direct push、force push、stale review／head、同名 spoofed status 的 negative run；
- private Environment approval、rejection、self-review與bypass-disabled runs；
- webhook signature、replay、idempotency、timeout、fork與mixed-diff regression；
- public surfaces privacy scan；
- public check／private attestation／Approval artifact digest correlation；
- full AGENTS.md baseline、cross-platform CI、drift與Kit package round trip。

## External Platform References

- GitHub rulesets and required status checks：<https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets>
- GitHub deployment environments：<https://docs.github.com/en/actions/concepts/workflows-and-actions/deployment-environments>
- GitHub environment protection rules：<https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments>
- GitHub checks API：<https://docs.github.com/en/rest/checks/runs>
- GitHub webhook validation：<https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries>

## Human Decision

2026-07-17 Human以HD-004-01～05接受本Design、ADR-002、L3 controls與credential custody baseline，並只授權TASK-008 sandbox implementation。TASK-009仍須獨立驗證；production Mode B、formal Approval merge與TASK-005未授權，Mode B維持fail closed。
