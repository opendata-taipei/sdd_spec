# 20 Starter Kit Packaging and Verification v1.5

## Purpose

本規範定義 Starter Kit v1.5 的可重現封裝、完整性驗證與安全解壓流程。`KIT_MANIFEST.json` 是唯一發布 allowlist；Git history、本機設定、runtime reports、研究附件與私有身分 overlay 不屬於發布包。

## Build

```bash
python scripts/build_kit_manifest.py --check
python scripts/package_starter_kit.py build
```

預設輸出至已由 Git 忽略的 `dist/`：

- `sdd-agentic-starter-kit-<version>.zip`
- `sdd-agentic-starter-kit-<version>.metadata.json`
- `sdd-agentic-starter-kit-<version>.zip.sha256`

封裝器只讀取 Manifest 列出的 regular files，不跟隨 symlink 或 junction。核准文字格式會移除 UTF-8 BOM 並正規化成 LF；其他檔案保持原始 bytes。ZIP 使用固定時間、Unix `0644`、`ZIP_STORED` 與 canonical entry order，因此 archive filename 以外的執行環境差異不影響 ZIP bytes。

Repository 的 `.gitattributes` 另強制文字檔在 Windows／Linux 都以 LF checkout，涵蓋 `Makefile` 與 `CODEOWNERS` 等無副檔名文字輸入；此政策是相同 commit 能產生相同 source bytes 的前置條件。

既有輸出預設不覆寫；只有維護者明確提供 `--force` 才可替換。

## Verify and Extract

```bash
python scripts/package_starter_kit.py verify \
  dist/sdd-agentic-starter-kit-1.5.0-dev.zip \
  --destination dist/verified \
  --run-governance
```

Verifier 依序檢查 canonical metadata、checksum、archive SHA-256、ZIP profile、路徑、entry set、size、CRC 與逐檔 SHA-256。所有 entry 驗證完成前不寫出內容；通過後才解壓至目的地同層 staging directory，治理檢查成功後再 rename 發布。失敗時 staging 會被清除，且既有目的地永不覆寫。

`--run-governance` 在無 `.git` 的 staging 目錄執行：

1. Kit Manifest `--check`
2. SDD structure validation
3. Enterprise approval/evidence validation
4. AI/tool portability validation

## Security Boundary

- ZIP 與兩個 sidecars 全部視為不可信輸入。
- 拒絕 absolute、UNC／drive、dot segment、backslash、NUL、Windows ADS colon、directory、symlink、encrypted 與非 regular entry。
- 拒絕 Unicode NFC／casefold collision、尾端 dot／space與 Windows device names。
- Verifier hard limits：4096 entries、每檔 32 MiB、總量 256 MiB；metadata 不得放寬限制。
- SHA-256 證明內容完整性，不證明發布者身分；需要 authenticity 時應另加可信 artifact signing。

## Skills Layout

Starter Kit 的 repo-scoped skills 位於 `.agents/skills/`，每組以 `SKILL.md` 作為可發現入口，並可保留工具中立的 `skill.yaml` contract。Codex 會直接掃描此 repo 路徑；其他 Agent 可將同一內容當作一般 Markdown／YAML workflow 讀取。

根目錄 `.skills/` 屬本機工具或 artifact 工作區，刻意不列入 Kit Manifest，避免將機器特定依賴混入發布包。

## CI Evidence

Linux 與 Windows job 分別 build、verify、執行無 Git round trip 並上傳三個發布檔。後續 comparison job 必須確認兩個平台的 checksum 完全一致，否則 release gate 失敗。

## Rollback

若跨平台 checksum、路徑安全或無 Git 治理檢查失敗，不發布 v1.5 artifact。回滾 package workflow／CLI 即可；v1.4.1 Manifest 與企業治理能力不受影響。
