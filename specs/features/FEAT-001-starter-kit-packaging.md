# FEAT-001：Starter Kit Packaging and Verification

- Status：In Progress
- Owner：Justin
- Target Release：v1.5.0
- Primary Change：CHG-2026-002

## Problem

目前 Starter Kit 可從 repository 使用，但導入者仍需自行判斷哪些檔案屬於正式發布內容。研究附件、本機 Codex 設定、runtime reports 與私有部署 overlay 不應混入可攜式發布包。

## User Value

維護者可以用單一命令建立可驗證發布包；導入者可在沒有 `.git` 的環境確認內容完整、版本正確且未遭增刪或竄改。

## In Scope

- 依 `KIT_MANIFEST.json` 建立 deterministic ZIP。
- 產生位於 ZIP 外部的 SHA-256 checksum 與機器可讀發布中繼資料 sidecars。
- 驗證 ZIP 檔案集合、每檔 hash、路徑安全與 Manifest 版本。
- 解壓後在無 `.git` 環境執行 Manifest、SDD、Enterprise 與 Portability checks。
- Windows／Linux package round-trip tests。
- 將可攜式 repo skills 發布於 `.agents/skills/`，並排除本機 `.skills/` cache。
- 發布包不得包含真實 GitHub login、Email、Token、私有 IAM mapping 或 runtime artifacts。

## Out of Scope

- 套件註冊中心、安裝程式 GUI 或自動更新服務。
- 真實企業 IAM、CODEOWNERS 或 Secret 注入。
- 將研究來源文件納入正式發布包。
- 對下游專案進行破壞性覆寫或自動 migration。

## Acceptance Outcomes

1. 相同 commit 與版本在支援平台產生相同 ZIP bytes 與 SHA-256。
2. ZIP 只包含 Manifest 列出的正式發布檔案；package metadata 與 checksum 為外部 sidecars。
3. 遺失、多出、內容 hash 不符、absolute path 或 `..` traversal 時驗證失敗。
4. 解壓後不依賴 `.git` 即可完成核心治理驗證。
5. CI 保存 archive、checksum、verification report 與 run URL。

## Security and Privacy Boundaries

- 封裝器只讀取 repo root 內受管檔案，不跟隨逃逸 root 的 symlink。
- ZIP entry 必須是正規化 POSIX relative path。
- 公開 package 僅包含 placeholder；私有 overlay 由導入方另行管理。
- Checksum 用於完整性驗證，不等同發行者身分簽章；正式企業可另加 artifact signing。

## Related Changes

| Change | Purpose | Status |
|---|---|---|
| CHG-2026-002 | 建立 deterministic package、verification 與 CI evidence | Implementing |

## Dependencies

- FEAT-001 依賴 v1.4.1 的 repo-root layout 與 Kit Manifest Gate。
- Python 3.12+ standard library；不新增封裝 runtime dependency。

## Risks

| Risk | Mitigation |
|---|---|
| ZIP timestamp／permission 造成跨平台 hash 不同 | 固定 timestamp、compression、permission 與排序 |
| Path traversal 或 symlink 逃逸 | resolve root boundary，拒絕 absolute／`..` entry |
| Manifest 漏列發布檔案 | CI Manifest Gate 與 package round-trip test |
| 將公開 checksum 誤認為簽章 | 文件明確區分 checksum 與 artifact signing |

## Release History

| Version | Status | Change | Notes |
|---|---|---|---|
| v1.5.0 | Planned | CHG-2026-002 | Initial packaging and verification capability |
