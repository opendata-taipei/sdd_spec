# CHG-2026-002 Technical Design

## Design Summary

新增標準函式庫 CLI，build 模式讀取 `KIT_MANIFEST.json` allowlist，驗證每個來源路徑位於 repo root 且不是 symlink escape，對核准文字類型正規化 LF bytes，再以固定 ZIP metadata 寫入排序後 entries。ZIP、package metadata JSON 與 `.sha256` 均為平行輸出，避免 archive hash 自我參照。verify 模式先 streaming 驗證 checksum、metadata、中央目錄、size 與 hash，再於新建 temporary directory 安全解壓並重跑核心 validators。

## Artifact Contract

- Base name：`sdd-agentic-starter-kit-<kit-version>`，版本字串只允許 ASCII alphanumeric、dot、hyphen。
- Outputs：`.zip`、`.metadata.json`、`.zip.sha256`；三個檔案必須以 exclusive create 寫入，除非使用者明確提供 `--force`。
- Metadata JSON：UTF-8、LF、`sort_keys=True`、`separators=(",", ":")`，結尾單一 LF。
- Checksum sidecar：小寫 64 字元 SHA-256、兩個空白、ZIP basename、單一 LF。
- ZIP profile：`ZIP_STORED`、archive comment 空、無 directory entry、entry extra/comment 空、`create_system=3`、regular-file `0644`、timestamp `1980-01-01T00:00:00`。
- Entry order 與 metadata entry order 均使用 `(path.casefold(), path)`；archive filename 不影響 ZIP bytes。

## Metadata Contract

- `format_version`：初版固定 `1.0`。
- `kit_version`：必須等於封裝時 `KIT_MANIFEST.json` 的 version。
- `source_manifest_sha256`：archive 內 canonical `KIT_MANIFEST.json` entry bytes 的 SHA-256。
- `archive`：basename、SHA-256、entry count、total uncompressed size。
- `entries`：每項只含 path、size、SHA-256，且集合與 Kit Manifest files 完全一致。
- JSON Schema 禁止 additional properties；整數不得為負數。

## Path Safety Rules

- Entry path 必須已是 Unicode NFC、POSIX relative path，且 round-trip 正規化後完全相同。
- 拒絕空字串、NUL、backslash、leading slash、UNC、drive prefix、`.`／`..` segment、空 segment、trailing slash。
- 拒絕 segment 尾端 dot／space，以及 Windows reserved device names（CON、PRN、AUX、NUL、COM1～9、LPT1～9，含副檔名形式）。
- 同時拒絕 exact duplicate 與 `NFC(path).casefold()` collision，避免 Windows／macOS 解壓覆寫。
- Build 端拒絕任何 symlink；每個 source resolve 後必須位於 repo root 且為 regular file。

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

- Text suffixes：`.md`、`.txt`、`.json`、`.jsonl`、`.yaml`、`.yml`、`.py`、`.toml`、`.ini`、`.cfg`；exact basenames：`.editorconfig`、`.gitignore`。
- 文字輸入必須可解碼為 UTF-8；BOM 移除，CRLF／CR 正規化為 LF。
- 其他檔案一律視為 binary 並保持 bytes 不變。
- ZIP 不寫 directory entries；每個 Manifest path 必須對應一個 regular-file entry。

## Verification Phases

1. 解析並 schema validate metadata；解析 checksum sidecar，驗證三個 basename 關係。
2. Streaming 計算 ZIP SHA-256，比對 metadata 與 checksum sidecar。
3. 讀取 central directory，套用 hard limits 與 path rules；拒絕 encrypted、directory、symlink、duplicate／collision。
4. 比對 Kit Manifest entry 與 metadata entry set；驗證 source Manifest hash 與 kit version。
5. Streaming 讀取每個 entry，驗證 declared size、actual bytes、CRC 與 SHA-256，不寫出檔案。
6. 全部通過後解壓至 destination 同層 staging directory；逐檔使用 exclusive create，再以 atomic rename 發布 destination。
7. 任一失敗刪除 staging；既有 destination 不得被覆寫，除非未來另開具 rollback contract 的 Change。

## Independent Resource Limits

- `MAX_ENTRIES = 4096`
- `MAX_ENTRY_SIZE = 32 MiB`
- `MAX_TOTAL_SIZE = 256 MiB`
- metadata 宣告值不得放寬上述 verifier hard limits。
- Streaming buffer 固定上限，不將完整 archive 或大型 entry 載入記憶體。

## Exit Codes

- `0`：成功。
- `2`：CLI 使用方式或本機 I/O 錯誤。
- `3`：格式、完整性、安全或治理驗證失敗。

## ADR

- ADR 待 G3 決定；若 deterministic archive contract 成為長期公開介面，建立 ADR-001。
