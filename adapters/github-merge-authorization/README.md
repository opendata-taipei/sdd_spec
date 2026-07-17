# GitHub Merge Authorization Adapter Contract

本Adapter是TASK-008的public sandbox scaffold，不是已部署的GitHub App，也不保存App ID、private repository、reviewer或IAM mapping。

## Trust Boundary

- GitHub App endpoint負責驗證`X-Hub-Signature-256`、以installation token讀取current PR與寫入check。
- `scripts/merge_authorization.py`負責strict diff classification、canonical request、replay、private attestation verification與public output allowlist。
- private control repository的protected Environment負責真實Change Manager review、separation-of-duties及attestation key access。
- public ruleset負責要求指定App來源的`approval-merge-authorization`；Adapter不得merge PR。

## Required GitHub App Configuration

Repository permissions：

| Permission | Access |
|---|---|
| Metadata | Read |
| Pull requests | Read |
| Contents | Read |
| Checks | Write |

不得授與Administration write、Contents write、Pull requests write或Members read。訂閱`pull_request` opened／reopened／synchronize事件；merge queue不在TASK-008 sandbox相容範圍。

## Request Handling

1. 在解析JSON前讀取bounded raw webhook bytes並呼叫`validate_webhook_signature`。
2. 以private `ReplayStore` claim `X-GitHub-Delivery`；相同delivery/request為idempotent duplicate，不同request為replay rejection。
3. 以installation token重新讀取PR current head、base與完整file list，不把webhook payload當作唯一真相。
4. 逐檔取得status、size、blob SHA-256、symlink／submodule flags；Approval candidate另讀取exact blob bytes，並從fresh checkout建立enterprise policy與known Evidence ID context。
5. 呼叫`build_authorization_request`。非Approval PR立即以`build_public_check_output`回報明確`not_applicable` success。
6. Approval PR先建立in-progress check，將canonical request送private control plane；不得把App token、reviewer或private repository metadata放入request。
7. private Environment review後取得attestation；重新讀取current head/base與enterprise policy，再呼叫`verify_attestation`。
8. `build_public_check_output`內部再次驗證attestation HMAC、current head/base與policy digest後才產生success payload；App以Checks API寫到request的exact head SHA。

所有exception只可公開穩定error code，不可dump webhook、Approval content、attestation、HTTP headers或private workflow reference。

## Required Check Mapping

Public check UI可顯示：

- name：`approval-merge-authorization`
- status：queued／in_progress／completed
- conclusion：success或failure（queued／in_progress不設conclusion）
- summary：只序列化`build_public_check_output`的allowlisted fields

無attestation、timeout、private rejection、API error或stale head不得使用neutral／skipped／success。Ruleset expected source必須由private overlay替換`config/merge-authorization-policy.json` placeholder並鎖定實際App ID。

## Private Inputs

下列名稱僅是contract labels，真值不得放入public repository：

- `SDD_GITHUB_APP_PRIVATE_KEY`
- `SDD_MERGE_WEBHOOK_SECRET`
- `SDD_MERGE_ATTESTATION_KEY_B64`
- private Environment reviewer／role mapping
- replay store與private audit destination

## Mode Boundary

本Adapter不代表SEC-F-009～015已closed。GitHub App installation、ruleset source pinning、protected Environment review與negative platform runs必須由TASK-009獨立驗證；在此之前Mode B維持fail closed。
