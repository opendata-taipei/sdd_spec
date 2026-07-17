# Private Merge Authorization Sandbox Runbook

## Purpose

本Runbook執行CHG-2026-003 TASK-008的sandbox-only setup。它落實REQ-MERGE-AUTHZ-001、REQ-APPROVAL-PR-001、SEC-MERGE-PRIVACY-003、OPS-MERGE-REL-004與ADR-002，但不授權production Mode B、formal Approval merge或TASK-005。

## Preconditions

- HD-004-01～05已由Human接受；Mode B implementation依L3 controls。
- 使用private sandbox repository／private deployment overlay與synthetic Change／Approval。
- Security Owner、Repository Admin、Change Manager、Secret Custodian及獨立Security Reviewer已在private overlay指派。
- 不把真實login、Email、numeric actor ID、Team、App private key、webhook secret、attestation key或private repository名稱貼入public issue、PR、Actions log或本Kit。

## 1. Create the Private Control Boundary

1. 建立private sandbox repository；禁止fork，限制administration與Actions log access。
2. 建立Environment `sdd-merge-authorization`，設定required reviewers、prevent self-review與disallow administrator bypass。
3. Environment secrets只保存private references／values：App private key、webhook secret、32-byte canonical Base64 attestation key及private audit target。
4. reviewer／role mapping只存在private IAM或Environment deployment overlay；public `CODEOWNERS`保持placeholder。

完成後由Change Manager在private audit確認設定，但public Evidence只保存去識別設定digest與pass／fail，不保存reviewer list。

## 2. Register the Sandbox GitHub App

依`adapters/github-merge-authorization/README.md`只授與Metadata read、Pull requests read、Contents read、Checks write。不得授與merge、Administration write、Contents write、Pull requests write或organization membership read。

啟用webhook secret與TLS endpoint，訂閱`pull_request` lifecycle。private key與webhook secret由Secret Custodian保存；App Operator只能取得執行所需reference，不把raw key寫入repository或runner artifact。

在private overlay填入App ID／installation scope；public `config/merge-authorization-policy.json`的`REPLACE_WITH...`必須保留，避免Starter Kit誤連到真實App。

## 3. Deploy the Controller

controller SHALL：

1. bounded-read raw webhook並以constant-time SHA-256 HMAC驗證；
2. 使用private、owner-only、非symlink／junction replay store；
3. 以short-lived installation token fresh-read current PR head/base/diff／Approval blob；
4. 呼叫`merge_authorization.py`產生canonical request；
5. 對Approval request觸發private Environment review，不將身分資料帶回public；
6. 驗證attestation後fresh-read head/base，僅對相同head寫check；
7. 對exception、timeout、rejection與stale state維持pending或failure；
8. 不呼叫merge API。

建議controller deployment使用immutable artifact digest、read-only filesystem（replay／audit volume除外）、egress allowlist、短timeout、bounded retry與private security telemetry。具體平台由private deployment policy決定。

## 4. Configure a Sandbox Ruleset

只在sandbox repository／test branch設定：

- require PR與至少一個非作者review；
- dismiss stale reviews、require approval of most recent push；
- strict required checks；
- required `approval-merge-authorization` expected source鎖定sandbox App；
- block deletion／force push；
- bypass actors為空。

不要先套用到本public repository的production default branch。匯出ruleset JSON後先執行privacy scan，再以artifact digest保存於private Evidence store。

## 5. TASK-008 Developer Tests

```bash
python -m unittest discover -s tests -p test_merge_authorization.py -v
python scripts/validate_sdd.py
python scripts/validate_enterprise.py
python scripts/build_kit_manifest.py --check
python scripts/drift_check.py --change CHG-2026-003
```

Developer可執行synthetic positive、invalid HMAC、duplicate/replay、mixed diff、modified Approval、stale head/base、expired／denied attestation與public-output privacy tests。不得把這些結果自行當作TASK-009 independent sign-off。

## 6. Stop／Rollback

發現key exposure、public identity、unexpected success或check source mismatch時：

1. disable sandbox App／revoke affected key；
2. 保留required check使merge freeze；
3. 停止private dispatch並保存去識別audit digest；
4. rotation後使全部pending attestation失效；
5. 修復後以current head建立新request並重新review。

不得以移除ruleset、設定bypass、公開mapping或人工建立同名status作rollback。

## 7. Handoff to TASK-009

handoff只包含sandbox identifiers的opaque digest、App permission/ruleset export digest、request／attestation fixtures、test log hash與public privacy scan。獨立Security Reviewer／QA須另執行TEST-RULESET-001、TEST-MERGE-FAIL-001、TEST-MERGE-REPLAY-001及TEST-MERGE-PRIVACY-001。

TASK-009完成前SEC-F-009～015保持Open，Mode B保持fail closed；production activation需新的Human Decision。
