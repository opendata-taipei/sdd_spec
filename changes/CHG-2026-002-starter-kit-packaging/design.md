# CHG-2026-002 Technical Design

## Design Summary

新增標準函式庫 CLI，build 模式讀取 `KIT_MANIFEST.json` allowlist，驗證每個來源路徑位於 repo root 且不是 symlink escape，再以固定 ZIP metadata 寫入排序後 entries。verify 模式先驗證 archive checksum 與中央目錄，再於暫存目錄安全解壓並重跑核心 validators。

## Requirement Mapping

| Design ID | Requirement | 設計內容 |
|---|---|---|
| DES-001 | REQ-PACKAGE-001, OPS-REL-002 | deterministic ZIP writer：固定 timestamp、Unix mode、compression level、UTF-8 path 與排序 |
| DES-002 | REQ-PACKAGE-VERIFY-001, SEC-PACKAGE-001 | fail-closed verifier：checksum、duplicate、absolute／drive／`..`、entry set 與 per-file hash |
| DES-003 | REQ-PACKAGE-PORTABLE-001, NFR-PERF-002 | 在 temporary directory round-trip 解壓，移除 Git context，執行核心治理檢查 |

## Current / Target Architecture

`KIT_MANIFEST → source boundary validation → deterministic ZIP + metadata + SHA256 → safe verifier → temporary extraction → governance checks`

## API／Event／Data Contract

CLI 預計提供 `build` 與 `verify` 子命令。Package metadata 至少包含 format version、kit version、archive SHA-256、entry count、每檔 path／SHA-256。Schema 使用 JSON 且禁止額外欄位。

## Security & Privacy

所有 archive path 視為不可信。驗證前不寫出 entry；解壓只能寫入新建 temporary directory。Checksum 只提供 integrity，公開文件不得宣稱具備 publisher authenticity。

## Migration & Rollback

v1.5.0 新增能力，不改變既有 Manifest contract。Rollback 為移除 package workflow 與 CLI；v1.4.1 repository workflow 保持可用。

## Alternatives

| Option | 優點 | 缺點 | 結論 |
|---|---|---|---|
| A：Python standard library ZIP | 無 runtime dependency、可攜 | 必須自行固定 metadata | 採用 |
| B：平台 shell zip | 簡單 | Windows/Linux metadata 與參數不一致 | 不採用 |
| C：第三方 packaging library | 功能完整 | 增加 supply-chain dependency | 暫不採用 |

## ADR

- ADR 待 G3 決定；若 deterministic archive contract 成為長期公開介面，建立 ADR-001。
