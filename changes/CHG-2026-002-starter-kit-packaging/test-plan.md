# CHG-2026-002 Test Plan

## Entry Criteria

- [ ] Requirement 與 Design 已核准
- [ ] Test Environment 與 Data 可用

## Test Cases

| Test ID | Requirement | Level | Scenario | Expected | Evidence |
|---|---|---|---|---|---|
| TEST-PACKAGE-001 | REQ-PACKAGE-001 | Integration | 依 Manifest 建立 archive | entry set、metadata、checksum 正確 | unittest／package report |
| TEST-PACKAGE-002 | REQ-PACKAGE-001, OPS-REL-002 | Reproducibility | 相同 fixture build 兩次並跨 OS 比較 | ZIP bytes 與 SHA-256 完全一致 | Windows/Linux CI artifact |
| TEST-PACKAGE-003 | REQ-PACKAGE-VERIFY-001 | Negative | 竄改、遺失、多出或 duplicate entry | verify fail closed | unittest output |
| TEST-PACKAGE-004 | SEC-PACKAGE-001 | Security | absolute、drive、`..`、symlink escape fixture | 不寫出目標目錄且回傳非 0 | security test report |
| TEST-PACKAGE-005 | REQ-PACKAGE-PORTABLE-001 | Round trip | 無 `.git` 解壓目錄執行核心 validators | 全部回傳 0 | CI log |
| TEST-PACKAGE-006 | NFR-PERF-002 | Performance | 目前 Manifest 規模 build／verify | 各 10 秒內 | CI timing |
| TEST-PACKAGE-007 | REQ-PACKAGE-001, OPS-REL-002 | Canonicalization | LF／CRLF／CR 與 UTF-8 BOM 文字 fixture、binary fixture | 文字 archive bytes 相同；binary bytes 不變 | unittest output |
| TEST-PACKAGE-008 | REQ-PACKAGE-VERIFY-001, SEC-PACKAGE-001 | Resource safety | encrypted、directory、NUL、backslash、entry count／size mismatch 與 oversized fixture | verify fail closed，目的目錄保持不存在或為空 | security test report |

## Exit Criteria

- [ ] 所有 Must Requirement 已通過
- [ ] 無未接受的 Critical／High Defect
- [ ] 測試證據已保存
