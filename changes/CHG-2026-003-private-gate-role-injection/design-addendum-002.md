# CHG-2026-003 Design Addendum 002：Verification-only Bootstrap Boundary

- Status：Proposed — Human Decision Required
- Date：2026-07-15
- Risk Level：L2
- Affected Design：DES-WORKFLOW-001、DES-REMEDIATION-001、Migration／Rollback
- Requirements：REQ-GATE-WORKFLOW-001 AC-016、REQ-STATE-REMEDIATION-001、SEC-PRIVACY-002、OPS-REL-003
- Findings：PILOT-F-001、PILOT-F-002、SEC-F-006、SEC-F-007

## Context and Findings

Protected Environment success run `29354763421` 已證明 Environment reviewer、OIDC identity、private role mapping、pepper、single-artifact contract、schema validation、cleanup 與 success-run privacy controls可運作。該 run 產生的 artifact 尚未合併，因此不構成 Repository 正式 Approval，也未驅動 state transition。

Pilot preflight 同時發現：

1. `main` 尚無 classic branch protection 或 branch ruleset（PILOT-F-001／SEC-F-006）。
2. 公開 `.github/CODEOWNERS` 仍是 Starter Kit placeholder；若直接填入真實 GitHub user／private Team mapping，會與公開 Kit 的最小揭露規則衝突（PILOT-F-002／SEC-F-007）。
3. Human 指示暫時忽略 branch rules。此指示可縮小目前執行範圍，但不能自行 supersede AC-016、接受 residual risk 或把未受保護 merge 視為正式 Gate。

## Proposed Operating Modes

### Mode A — Verification-only

在下列控制成立時，允許執行 TEST-WORKFLOW-001／002 與 TEST-PRIVACY-001 的外部 workflow 測試：

- `sdd-approval` Required reviewers 與 Prevent self-review 開啟，administrator bypass 關閉。
- Protected role map 與 pepper 只存在 Environment secrets。
- Dispatch 使用已核准 Change／Gate／Evidence IDs，artifact 綁定當下完整 commit SHA。
- Artifact 與 raw logs 只在 ignored runtime location 做 digest、schema、entry-set 與 privacy scan。
- 測試 Evidence 可放在 feature branch，但不得把產生的 Approval JSON 加入 `changes/*/approvals/`。

Mode A 明確禁止：

- 將 workflow artifact 宣稱為 merged Approval 或 Gate passed。
- 合併 Approval、append `STATE_TRANSITIONED`、修改衍生 state 或開始下一個正式 Gate remediation。
- 以 direct push、administrator bypass 或對話核准取代 PR／merge controls。
- 將真實 login、Email、actor mapping、pepper、JWT、raw logs 或 private Team mapping加入公開 Repository／Kit。

### Mode B — Formalization

正式 G1～G4 bootstrap 與 TASK-005 remediation 只能在 AC-016 merge controls 可驗證後進行。至少必須有：

- `main` 的 effective branch protection／ruleset，要求 Pull Request 與 Human approval，禁止 force push／delete，且不得以 administrator bypass 繞過。
- 可驗證的 Change Manager merge authorization 與 reviewer separation。
- CODEOWNERS 或經 Requirement／Security re-baseline 核准的等效控制。
- Approval artifact 以單檔 PR 合併，合併後才執行 Enterprise validation 與逐步 append-only transition。

本 Addendum 不提供 AC-016 exception，也不定義 generic PR approval 為 CODEOWNERS 的自動等價物。若公開 Repository 不允許揭露真實 CODEOWNERS mapping，必須擇一：

1. 在不列入公開 Kit 的 private deployment repository／overlay 實作正式 CODEOWNERS；或
2. 建立 Requirement Addendum 與 Security re-review，定義不揭露 IAM mapping 的可驗證替代控制，再重新取得適用 Gate。

## Security Review Addendum

| ID | Severity | Finding | Required disposition |
|---|---|---|---|
| SEC-F-006 | Medium | 無 branch protection／ruleset 時，direct push、force push 或未經審查 merge 無平台強制阻擋。 | Mode A 可繼續不可合併的測試；Mode B fail closed。不得把此狀態記為 risk accepted。 |
| SEC-F-007 | Medium | 公開 CODEOWNERS 若填真實 user／private Team 會揭露治理身分關係；保留 placeholder 又無法形成正式 merge control。 | 使用 private deployment boundary，或經 Requirement／Security re-baseline 核准替代控制；不得把真實 mapping 寫入公開 Kit。 |

這兩項 finding 不影響 run `29354763421` 作為 TEST-WORKFLOW-001 success-path 與 privacy scan Evidence 的有效性，但阻擋 Approval merge、state remediation、G5 submission 與 Release readiness。

## Verification Plan Update

Addendum 核准後，Mode A 下一步可執行：

1. 使用不存在於 policy 的 Gate ID 執行 protected Environment failure run，預期 identity resolver 非 0 且無 artifact；不修改正式 secrets。
2. Cancellation run，確認 `if: always()` cleanup 可觀察；hard cancellation 仍以 GitHub-hosted ephemeral runner disposal 為最終邊界。
3. Missing-secret／invalid-mapping／existing-target tests 維持已通過的 local synthetic harness；若要做 real Environment run，必須另建不含正式 secrets 的 sandbox Environment 並取得 Platform／Security 授權。
4. 對每次 external run 掃描 artifact absence、raw logs 與 secret masking，保存獨立 Evidence。

上述測試不得使用或輸出 secret 值，不得修改 role map 來製造未經授權角色，也不得由 Agent 代替 Environment reviewer。

## Rollback and Expiry

- 任一 privacy、identity、cleanup、artifact-count 或 context-binding finding 立即停用 workflow，依原 Release Plan rollback。
- Verification artifacts 到期或 triggering commit 不再是 formalization baseline 時，必須重新產生，不得改寫舊 artifact。
- Addendum 被拒絕時，停止額外 external runs，回到原 Design：先完成 branch protection／CODEOWNERS controls。

## Human Decision

`HUMAN_DECISION_REQUIRED`：

- 核准 Addendum 002：接受 Mode A verification-only 邊界，允許繼續 negative／cancellation Evidence；同時確認 Mode B 仍 fail closed，這不是 branch protection／CODEOWNERS risk acceptance。
- 或拒絕 Addendum 002：停止 external workflow tests，先完成 AC-016 controls。
