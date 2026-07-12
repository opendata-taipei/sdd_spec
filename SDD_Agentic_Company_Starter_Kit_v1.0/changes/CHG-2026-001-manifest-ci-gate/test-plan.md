# CHG-2026-001 Test Plan

## Entry Criteria

- [ ] Requirement 與 Design 已核准
- [ ] Test Environment 與 Data 可用

## Test Cases

| Test ID | Requirement | Level | Scenario | Expected | Evidence |
|---|---|---|---|---|---|
| TEST-MANIFEST-001 | REQ-MANIFEST-001 | Integration | Manifest 與檔案樹一致 | 回傳 0，顯示版本與檔案數 | CI log |
| TEST-MANIFEST-002 | REQ-MANIFEST-001, OPS-REL-001 | Negative | fixture 新增未列入 Manifest 的檔案 | 回傳 1，提示重建命令；Windows/Linux 結果一致 | unittest output |
| TEST-MANIFEST-003 | NFR-PERF-001, SEC-APP-001 | Non-functional | 執行 check 並比較執行前後 Git 狀態 | 5 秒內完成且工作區無新增修改 | CI timing、git diff |

## Exit Criteria

- [ ] 所有 Must Requirement 已通過
- [ ] 無未接受的 Critical／High Defect
- [ ] 測試證據已保存
