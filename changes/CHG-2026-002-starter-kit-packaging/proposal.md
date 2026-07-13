# CHG-2026-002 Change Proposal：Starter Kit Packaging

- Status：Draft
- Risk Level：`L2`
- Change Owner：`Justin`
- Product Owner：`Justin`

## 問題與背景

Starter Kit 已能在 repository root 通過治理與 Manifest 檢查，但缺少正式發布包與獨立驗證流程。導入者若直接下載整個研究 repository，可能混入研究附件、本機設定或 runtime artifacts，也無法確認解壓後內容是否完整。

## 目標與成功指標

- Objective：建立 deterministic、可驗證、無 `.git` 依賴的 Starter Kit 發布包。
- Metric：Windows／Linux 對相同 commit 產生相同 ZIP SHA-256；竄改與路徑攻擊測試全數被拒絕；解壓後核心治理檢查全部通過。

## 範圍

### In Scope

- FEAT-001 Feature Registry 與長期能力文件。
- 依 Kit Manifest 建立 ZIP、checksum 與 package metadata。
- 封裝與驗證 CLI、round-trip tests、CI artifacts 與操作文件。
- 公開包的身分資料與 runtime artifact 排除規則。

### Out of Scope

- 套件註冊中心、GUI installer、自動更新或下游專案覆寫。
- 真實 IAM／CODEOWNERS／Secret overlay。
- Artifact signing infrastructure；本次只定義 checksum extension point。

## 影響與風險

| 項目 | 影響 | 風險 | 緩解 |
|---|---|---|---|
| 跨平台 ZIP metadata | 相同內容可能產生不同 bytes | Medium | 固定 timestamp、permission、compression、排序與 UTF-8 path |
| ZIP path traversal | 惡意 entry 可能逃逸目的目錄 | High | 拒絕 absolute path、drive prefix、`..` 與 root 外 symlink |
| 發布內容洩漏 | 私有設定或 runtime report 被封裝 | Medium | 僅封裝 Manifest allowlist，加入敏感資料與排除測試 |
| Checksum 誤用 | 使用者誤認為發行者簽章 | Low | 文件區分 integrity checksum 與 authenticity signature |

## Gate G1

- [ ] Business Problem 已確認
- [ ] Scope／Out of Scope 已確認
- [ ] Risk Level 已核准
- [ ] Owner 與 Success Metric 已定義
