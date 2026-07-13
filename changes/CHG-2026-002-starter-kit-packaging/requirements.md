# CHG-2026-002 Requirements

## Functional Requirements

### REQ-PACKAGE-001

- Statement：WHEN 維護者執行 package build THEN 系統 SHALL 只依 `KIT_MANIFEST.json` 建立 deterministic ZIP、SHA-256 checksum 與 package metadata。
- Priority：Must
- Source：FEAT-001
- Acceptance Criteria：
  - AC-001：相同 commit、版本與受管檔案在 Windows／Linux 產生相同 ZIP bytes 與 SHA-256。
  - AC-002：ZIP 檔案集合與 Manifest 完全一致，不包含研究附件、本機設定、runtime reports 或私有 overlay。
  - AC-003：所有 entry 使用 POSIX relative path、固定 timestamp、permission、compression 與排序。

### REQ-PACKAGE-VERIFY-001

- Statement：WHEN 使用者驗證發布包 THEN 系統 SHALL 在不信任 ZIP entry 的前提下檢查 checksum、路徑安全、檔案集合與每檔內容 hash，並 fail closed。
- Priority：Must
- Source：FEAT-001
- Acceptance Criteria：
  - AC-004：ZIP checksum、metadata 或任一 entry 內容不符時回傳非 0。
  - AC-005：absolute path、drive prefix、`..` traversal、duplicate entry 或 root 外 symlink 被拒絕。
  - AC-006：驗證過程不得將未驗證 entry 寫出目標目錄。

### REQ-PACKAGE-PORTABLE-001

- Statement：WHEN 發布包在沒有 `.git` 的乾淨目錄解壓 THEN 系統 SHALL 能執行 Manifest、SDD、Enterprise 與 Portability validation。
- Priority：Must
- Source：FEAT-001
- Acceptance Criteria：
  - AC-007：round-trip fixture 移除 `.git` 後核心治理檢查全部回傳 0。
  - AC-008：封裝與驗證只依 Python 3.12+ standard library 執行。

## Traceability

| Requirement | Design | Task | Test | Status |
|---|---|---|---|---|
| REQ-PACKAGE-001 | DES-001 | TASK-001 | TEST-PACKAGE-001, TEST-PACKAGE-002 | Draft |
| REQ-PACKAGE-VERIFY-001 | DES-002 | TASK-002 | TEST-PACKAGE-003, TEST-PACKAGE-004 | Draft |
| REQ-PACKAGE-PORTABLE-001 | DES-003 | TASK-003 | TEST-PACKAGE-005 | Draft |
