# CHG-2026-003 Mode A Cancellation Workflow Run 29407591960

- Change：CHG-2026-003
- Requirements：REQ-GATE-WORKFLOW-001、SEC-PRIVACY-002、OPS-REL-003
- Tests：TEST-WORKFLOW-002 cancellation path、TEST-PRIVACY-001 cancellation-run portion
- Workflow：[SDD Gate Approval run 29407591960](https://github.com/opendata-taipei/sdd_spec/actions/runs/29407591960)
- Evidence job：[attempt 3 job 87327203920](https://github.com/opendata-taipei/sdd_spec/actions/runs/29407591960/job/87327203920)
- Event：`workflow_dispatch`
- Triggering commit：`e09289c70850b01c0a4928f1766338a7f5a419fb`
- Branch：`main`
- Attempt 3 completed：2026-07-15T10:20:05Z
- Result：pass for scoped cancellation path

## Authorized Scenario

依 Design Addendum 002 的 Mode A verification-only 邊界與 2026-07-15 Human authorization，使用合法 Change／Gate／Evidence inputs觸發 protected Environment workflow，並在 runner 開始執行後取消。此測試不授權合併 Approval、state transition、Gate pass 或 Mode B formalization。

## Attempt Separation

同一 GitHub Actions run 經過三次 attempts，必須分開判讀：

| Attempt | Job | Conclusion | Observation |
|---|---:|---|---|
| 1 | `87326706579` | success | identity、Approval creation、validation、cleanup 與 artifact upload steps 全部 success；取消時機未命中，因此不作 cancellation Evidence。該 Approval artifact 未下載、未合併、未加入 Repository，也不構成正式 Gate。 |
| 2 | `87326823339` | cancelled | runner 約執行 4 秒後取消；GitHub Jobs API 未提供 step metadata，不作 cleanup Evidence。 |
| 3 | `87327203920` | cancelled | pip install step 被取消；identity、Approval creation、validation 與 artifact upload skipped；cleanup step success。本 Evidence 以 attempt 3 為準。 |

目前 run artifacts API count 為 0。這只表示 attempts 完成後的目前狀態；不得用它改寫 attempt 1 的 upload step success 歷史。

## Attempt 3 Cancellation Controls

- Job started：2026-07-15T10:19:57Z；completed：2026-07-15T10:20:05Z。
- `Run python -m pip install -r requirements-governance.txt` conclusion：`cancelled`。
- `Prepare protected Gate identity`：`skipped`；未要求 OIDC token，也未注入 protected role map／pepper。
- `Create approval from trusted workflow context`：`skipped`。
- `Validate generated approval`：`skipped`。
- `Cleanup OIDC temporary file`：`success`；raw log 顯示 `rm -f "$RUNNER_TEMP/sdd-oidc-$GITHUB_RUN_ID.json"` 實際執行。
- `Run actions/upload-artifact@v4`：`skipped`。
- Raw logs 無 Approval JSON path 或 Approval payload。

Attempt 3 符合 TEST-WORKFLOW-002 對 runner-started cancellation、always cleanup 與無 partial Approval artifact 的 scoped預期。

## Raw Log Privacy Scan

Human 下載的 attempt 3 job logs 僅在 ignored top-level `tmp/` 做唯讀掃描；9 files、37,936 bytes，file-manifest digest：`97b766e76d31dc3e46b48a823669d774a0410683bcf80187ff108ec4526b9b97`。Raw logs 未保存至 Evidence、Git 或 Kit。

| Check | Result |
|---|---|
| Email／GitHub login／actor claim／raw actor ID | 0 finding |
| JWT／GitHub token／private key | 0 finding |
| Unmasked bearer／32-byte Base64 pepper candidate | 0 finding |
| Role-map content／protected secret assignments | 0 finding；identity step skipped，secrets 未進入 step environment |
| Approval path／payload | 0 finding |
| Cancellation error | expected `The operation was canceled.`；aggregate／step log 各一筆 |
| Cleanup command | present；aggregate／step log 各一筆 |
| Other warnings | Node.js 20 deprecation annotation duplicated in aggregate／completion logs；無 security control failure |

## Limits and Security Disposition

本 attempt 在 OIDC identity step 前取消，因此直接證明 cleanup step 在早期 cancellation 仍執行，但沒有建立 OIDC temp file可供刪除。Addendum 002 對「OIDC file 建立後的 hard cancellation」仍以 shell trap、`if: always()` 與 GitHub-hosted ephemeral runner disposal作最終邊界；本 Evidence 不把該不可觀察 disposal誤述為已直接驗證。

在此限制下，Mode A success、unknown-Gate negative 與 runner-started cancellation paths 均已有 external Evidence；TEST-WORKFLOW-002 與 TEST-PRIVACY-001 的 Addendum 002 scoped verification可記為通過。SEC-F-006／007、Mode B controls 與 TASK-005 formal remediation仍未完成。

本 run 及任何 attempt 均不是 merged Approval、Gate pass、risk acceptance 或 state transition Evidence。
