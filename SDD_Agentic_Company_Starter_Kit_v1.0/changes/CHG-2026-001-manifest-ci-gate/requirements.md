# CHG-2026-001 Requirements

## Functional Requirements

### REQ-MANIFEST-001

- Statement：WHEN SDD Quality Gates workflow 執行 THEN 系統 SHALL 以 `build_kit_manifest.py --check` 驗證 `KIT_MANIFEST.json` 與套件內容一致。
- Priority：Must
- Source：Starter Kit Maintainer
- Acceptance Criteria：
  - AC-001：Manifest 版本、檔案數量與完整清單正確時，命令回傳 0。
  - AC-002：新增或刪除受管檔案而未重建 Manifest 時，命令回傳非 0 並提示重建命令。
  - AC-003：CI 在 portability check 前執行此檢查，且不修改工作區。

## Traceability

| Requirement | Design | Task | Test | Status |
|---|---|---|---|---|
| REQ-MANIFEST-001 | DES-001 | TASK-001 | TEST-MANIFEST-001, TEST-MANIFEST-002 | Draft |
