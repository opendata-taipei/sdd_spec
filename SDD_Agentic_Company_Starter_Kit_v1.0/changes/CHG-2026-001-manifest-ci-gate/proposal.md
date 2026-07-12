# CHG-2026-001 Change Proposal：Manifest Ci Gate

- Status：Draft
- Risk Level：`L2`
- Change Owner：`Justin`
- Product Owner：`Justin`

## 問題與背景

Starter Kit 已提供 `build_kit_manifest.py --check`，但 CI 尚未執行它。檔案新增、刪除或版本更新後，`KIT_MANIFEST.json` 仍可能在審查時未被發現已過期。

## 目標與成功指標

- Objective：在每次 Pull Request 與 main push 自動阻擋過期的 Kit Manifest。
- Metric：CI 能偵測 Manifest 版本、數量或檔案清單任一差異；正確 Manifest 的檢查維持通過。

## 範圍

### In Scope

- 在既有 SDD Quality Gates workflow 加入 Manifest check。
- 增加成功與失敗路徑的自動化測試。
- 補充維護者修復過期 Manifest 的操作說明。

### Out of Scope

- 不自動修改 Manifest 或提交修正。
- 不改變 Human Gate、Evidence、Approval 或發布權限。
- 不導入新的第三方 GitHub Action。

## 影響與風險

| 項目 | 影響 | 風險 | 緩解 |
|---|---|---|---|
| CI 執行時間 | 增加一次本機檔案掃描 | Low | 檢查不存取網路，目標完成時間低於 5 秒 |
| Manifest 漂移 | PR 會被阻擋 | Low | 錯誤訊息提供明確重建命令 |
| 路徑處理 | 不同 OS 的路徑表示可能不同 | Medium | Manifest 固定使用 POSIX 相對路徑並在 Windows/Linux 測試 |

## Gate G1

- [ ] Business Problem 已確認
- [ ] Scope／Out of Scope 已確認
- [ ] Risk Level 已核准
- [ ] Owner 與 Success Metric 已定義
