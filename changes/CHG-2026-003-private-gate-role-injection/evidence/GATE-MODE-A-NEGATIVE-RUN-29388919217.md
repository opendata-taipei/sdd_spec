# CHG-2026-003 Mode A Negative Workflow Run 29388919217

- Change：CHG-2026-003
- Requirements：REQ-GATE-RESOLVE-001、REQ-GATE-WORKFLOW-001、SEC-IDENTITY-002、SEC-PRIVACY-002、OPS-REL-003
- Tests：TEST-ROLE-003、TEST-WORKFLOW-002 unknown-Gate path、TEST-PRIVACY-001 failure-run portion
- Workflow：[SDD Gate Approval run 29388919217](https://github.com/opendata-taipei/sdd_spec/actions/runs/29388919217)
- Event：`workflow_dispatch`
- Triggering commit：`f66771dd8e01aadce3d1b05d35392e1bed028791`
- Branch：`design/chg-2026-003-addendum-002`
- Observed：2026-07-15T04:28:43Z
- Conclusion：failure（expected fail-closed result）

## Authorized Scenario

依已核准 Design Addendum 002 的 Mode A verification-only 邊界，由 Human reviewer 放行受保護的 `sdd-approval` Environment deployment，使用 policy 不存在的 Gate ID `G9_INVALID` 驗證 unknown-Gate failure path。正式 Environment secrets 未修改，且本次執行不授權合併 Approval、state transition 或 Mode B formalization。

## Observed Failure Path

GitHub Actions summary 與展開的 job annotation 顯示：

- workflow conclusion 為 `failure`，總時間 44 秒；`create-approval` job 執行 6 秒。
- `Prepare protected Gate identity` 以 `Gate identity preparation failed: unknown gate` 結束，process exit code 為 1。
- `Create approval from trusted workflow context` 與 `Validate generated approval` 未執行。
- `Cleanup OIDC temporary file` 的 `if: always()` cleanup step 有執行。
- Artifact upload 未執行；run summary 的 Artifacts 顯示 `–`，頁面沒有 artifact link。

結果符合 REQ-GATE-RESOLVE-001 AC-005 與 TEST-WORKFLOW-002 對 unknown Gate 的 fail-closed 預期，且未觀察到 partial Approval artifact。

## Raw Log Privacy Scan

Human 下載的 job log archive 僅在 ignored `tmp/` runtime location 接受唯讀掃描；10 files、41,685 bytes，file-manifest digest：`9e2dbb13c514929303b31ef0f8180fdcdb1dc474bfa598ee3c5acb457b7e7e55`。Raw logs 未保存至 Evidence 或 Kit。

| Check | Result |
|---|---|
| Email／GitHub login／actor claim／raw actor ID | 0 finding |
| JWT／GitHub token／private key | 0 finding |
| Unmasked bearer／32-byte Base64 pepper candidate | 0 finding；bearer 只出現在 shell variable reference |
| Role-map content | 0 finding |
| Protected Environment secrets | role map 與 pepper 在 aggregate／step logs 全部為 GitHub `***` masking |
| Approval payload／Approval JSON path | 0 finding |
| Identity failure | `unknown gate`，exit code 1；符合預期 |
| OIDC cleanup | shell trap 與獨立 cleanup command 均 present |
| Artifact upload | action repository 在 job setup 被下載，但 upload step 未執行、無 step log、run summary 無 artifact |

兩個 error 是 aggregate log 與 step log 重複記錄的預期 `unknown gate` failure。兩個 warning 是 aggregate log 與 completion log 重複記錄的 GitHub Actions Node.js 20 deprecation annotation；沒有額外安全控制失敗。本 Evidence 不保存 Environment reviewer identity 或其他 private IAM mapping。

## Security Finding

| ID | Severity | Requirement | Finding | Required control |
|---|---|---|---|---|
| SEC-F-008 | Medium | SEC-PRIVACY-002、OPS-REL-003 | `tmp/` 已受 `.gitignore` 排除，但 `scripts/build_kit_manifest.py` 仍會把實際存在的 raw logs 加入 `KIT_MANIFEST.json`；依目前 builder 執行 build 會把 private runtime evidence 放入公開 Kit allowlist。 | Builder 必須明確排除 top-level `tmp/`，加入 failure-path regression test，並重建／驗證 Kit Manifest。修正前不得以存在 raw logs 的 workspace 建立發布包。 |

目前 `KIT_MANIFEST.json` 已維持 0 個 `tmp/` entry，raw logs 也維持 ignored；因此 `python scripts/build_kit_manifest.py --check` 在 raw logs 存在時會 fail closed。修正 builder 與測試會新增本 Change 尚未 declared 的程式／測試檔案並改變 package control，需先取得 Human Decision；不得以手工忽略檢查或把 raw logs 納入 Manifest 解決。

## Result and Limits

本 Evidence 將 TEST-WORKFLOW-002 的 protected Environment unknown-Gate 子案例，以及 TEST-PRIVACY-001 的 failure-run raw-log／artifact-absence portion 記為通過；TEST-WORKFLOW-002 整體仍為 Partial。以下尚未完成：

- cancellation run 與其 cleanup／privacy Evidence。
- SEC-F-008 的 Kit builder runtime exclusion remediation。
- optional real Environment missing-secret／invalid-mapping／existing-target tests；依 Addendum 002，必須使用 sandbox Environment 並另取 Platform／Security 授權。
- Mode B 所需 branch protection／ruleset、merge authorization 與 CODEOWNERS 或已 re-baseline 的等效控制。

本 run 不是 Approval、Gate pass、risk acceptance 或 state transition Evidence。
