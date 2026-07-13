# CHG-2026-002 Technical Design

## Design Summary

新增標準函式庫 CLI，build 模式讀取 `KIT_MANIFEST.json` allowlist，驗證每個來源路徑位於 repo root 且不是 symlink escape，對核准文字類型正規化 LF bytes，再以固定 ZIP metadata 寫入排序後 entries。ZIP、package metadata JSON 與 `.sha256` 均為平行輸出，避免 archive hash 自我參照。verify 模式先 streaming 驗證 checksum、metadata、中央目錄、size 與 hash，再於新建 temporary directory 安全解壓並重跑核心 validators。

## Requirement Mapping

| Design ID | Requirement | 設計內容 |
|---|---|---|
| DES-001 | REQ-PACKAGE-001, OPS-REL-002 | deterministic ZIP writer：文字 LF canonicalization、1980-01-01 timestamp、Unix regular-file 0644 mode、`ZIP_STORED`、UTF-8 POSIX path 與 `(casefold, path)` 排序 |
| DES-002 | REQ-PACKAGE-VERIFY-001, SEC-PACKAGE-001 | fail-closed streaming verifier：sidecar checksum／schema、duplicate、absolute／UNC／drive／dot segment／backslash／NUL、symlink／encrypted、entry set、size limit 與 per-file hash |
| DES-003 | REQ-PACKAGE-PORTABLE-001, NFR-PERF-002 | 在 temporary directory round-trip 解壓，移除 Git context，執行核心治理檢查 |

## Current / Target Architecture

`KIT_MANIFEST → source boundary validation → deterministic ZIP + metadata + SHA256 → safe verifier → temporary extraction → governance checks`

## API／Event／Data Contract

CLI 預計提供 `build` 與 `verify` 子命令。輸出為 `<name>.zip`、`<name>.metadata.json` 與 `<name>.zip.sha256`。Package metadata 包含 format version、kit version、source Manifest SHA-256、archive SHA-256、entry count、total uncompressed size、每檔 path／size／SHA-256。Schema 使用 JSON 且禁止額外欄位；metadata 本身不放入 ZIP。

## Security & Privacy

所有 archive path 與 metadata 視為不可信。驗證前不寫出 entry；解壓只能寫入新建且為空的 temporary directory。檢查 entry count、逐檔與總 size 後才允許 streaming hash，以限制資源消耗。Checksum 只提供 integrity，公開文件不得宣稱具備 publisher authenticity。

## Migration & Rollback

v1.5.0 新增能力，不改變既有 Manifest contract。Rollback 為移除 package workflow 與 CLI；v1.4.1 repository workflow 保持可用。

## Alternatives

| Option | 優點 | 缺點 | 結論 |
|---|---|---|---|
| A：Python standard library ZIP | 無 runtime dependency、可攜 | 必須自行固定 metadata | 採用 |
| B：平台 shell zip | 簡單 | Windows/Linux metadata 與參數不一致 | 不採用 |
| C：第三方 packaging library | 功能完整 | 增加 supply-chain dependency | 暫不採用 |
| D：Deflate compression | 包體較小 | zlib 版本可能使跨平台 compressed bytes 不同 | v1.5.0 不採用，使用 ZIP_STORED |

## Canonical Content Policy

- Text suffixes：`.md`、`.txt`、`.json`、`.jsonl`、`.yaml`、`.yml`、`.py`、`.toml`、`.ini`、`.cfg`、`.editorconfig`、`.gitignore`。
- 文字輸入必須可解碼為 UTF-8；BOM 移除，CRLF／CR 正規化為 LF。
- 其他檔案一律視為 binary 並保持 bytes 不變。
- ZIP 不寫 directory entries；每個 Manifest path 必須對應一個 regular-file entry。

## ADR

- ADR 待 G3 決定；若 deterministic archive contract 成為長期公開介面，建立 ADR-001。
