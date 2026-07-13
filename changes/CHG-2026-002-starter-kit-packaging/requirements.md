# CHG-2026-002 Requirements

## Functional Requirements

### REQ-PACKAGE-001

- Statement：WHEN 維護者執行 package build THEN 系統 SHALL 只依 `KIT_MANIFEST.json` 建立 deterministic ZIP，以及位於 archive 外部的 SHA-256 checksum 與 package metadata sidecars。
- Priority：Must
- Source：FEAT-001
- Acceptance Criteria：
  - AC-001：相同 commit、版本與邏輯文字內容在 Windows／Linux 產生相同 ZIP bytes 與 SHA-256。
  - AC-002：ZIP entry 集合與 Manifest 完全一致；metadata 與 checksum 為 archive 外部 sidecars，不加入 ZIP。
  - AC-003：所有 entry 使用 POSIX relative path、固定 timestamp／permission、`ZIP_STORED`、排序；核准的文字副檔名在封裝時正規化為 UTF-8 LF bytes，二進位檔保持原始 bytes。
  - AC-009：metadata 包含 format version、kit version、source Manifest SHA-256、archive SHA-256、entry count，以及每個 entry 的 path、size 與 SHA-256；JSON 使用 UTF-8 LF、sorted keys 與固定 separators，checksum sidecar 使用 `<sha256>  <filename>` 格式。

### REQ-PACKAGE-VERIFY-001

- Statement：WHEN 使用者驗證發布包 THEN 系統 SHALL 在不信任 ZIP entry 的前提下檢查 checksum、路徑安全、檔案集合與每檔內容 hash，並 fail closed。
- Priority：Must
- Source：FEAT-001
- Acceptance Criteria：
  - AC-004：ZIP checksum、metadata schema、source Manifest hash、entry set 或任一 entry size／hash 不符時回傳非 0。
  - AC-005：absolute path、UNC／drive prefix、`.`／`..` segment、backslash、NUL、duplicate、directory、symlink 或 encrypted entry 被拒絕。
  - AC-006：驗證 SHALL 先以 streaming 方式完成結構、size 與 hash 檢查，再寫入新建且為空的目的目錄；失敗時不得留下部分解壓內容。
  - AC-010：entry count 必須等於 metadata 與 Manifest；總 uncompressed size 必須等於 metadata sizes 總和並受設定上限約束，以降低 ZIP bomb 風險。

### REQ-PACKAGE-PORTABLE-001

- Statement：WHEN 發布包在沒有 `.git` 的乾淨目錄解壓 THEN 系統 SHALL 能執行 Manifest、SDD、Enterprise 與 Portability validation。
- Priority：Must
- Source：FEAT-001
- Acceptance Criteria：
  - AC-007：round-trip fixture 移除 `.git` 後核心治理檢查全部回傳 0。
  - AC-008：封裝與驗證只依 Python 3.12+ standard library 執行，且輸出檔寫入 repo 外或明確忽略的 `dist/`。

## Traceability

| Requirement | Design | Task | Test | Status |
|---|---|---|---|---|
| REQ-PACKAGE-001 | DES-001 | TASK-001 | TEST-PACKAGE-001, TEST-PACKAGE-002, TEST-PACKAGE-007 | Draft |
| REQ-PACKAGE-VERIFY-001 | DES-002 | TASK-002 | TEST-PACKAGE-003, TEST-PACKAGE-004, TEST-PACKAGE-008 | Draft |
| REQ-PACKAGE-PORTABLE-001 | DES-003 | TASK-003 | TEST-PACKAGE-005 | Draft |
| NFR-PERF-002 | DES-003 | TASK-003 | TEST-PACKAGE-006 | Draft |
| SEC-PACKAGE-001 | DES-002 | TASK-002 | TEST-PACKAGE-004, TEST-PACKAGE-008 | Draft |
| OPS-REL-002 | DES-001 | TASK-001 | TEST-PACKAGE-002, TEST-PACKAGE-007 | Draft |
