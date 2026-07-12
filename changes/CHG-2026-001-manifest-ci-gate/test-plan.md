# CHG-2026-001 Test Plan

## Entry Criteria

- [x] Requirement 與 Design 已核准
- [x] Test Environment 與 Data 可用

## Test Cases

| Test ID | Requirement | Level | Scenario | Expected | Evidence |
|---|---|---|---|---|---|
| TEST-MANIFEST-001 | REQ-MANIFEST-001 | Integration | Manifest 與檔案樹一致 | 回傳 0，顯示版本與檔案數 | CI log |
| TEST-MANIFEST-002 | REQ-MANIFEST-001, OPS-REL-001 | Negative | fixture 新增未列入 Manifest 的檔案，並加入僅大小寫不同的路徑鍵值 | 回傳 1，提示重建命令；排序含確定 tie-breaker，Windows/Linux 結果一致 | unittest output |
| TEST-MANIFEST-003 | NFR-PERF-001, SEC-APP-001 | Non-functional | 執行 check 並比較執行前後 Git 狀態 | 5 秒內完成且工作區無新增修改 | CI timing、git diff |
| TEST-MANIFEST-004 | REQ-MANIFEST-001, OPS-REL-001 | Integration | 建立 Runtime／Eval／Test report 與本機 cache fixture | 排除項目不進入 Manifest，正式發布檔案仍被偵測 | unittest output |
| TEST-IDENTITY-001 | REQ-IDENTITY-PRIVACY-001 | Security review | 掃描公開設定、範例與文件中的 actor mapping | 僅出現虛構 actor／placeholder；無 Email、Token、完整 OIDC claims | Security review record |

## Exit Criteria

- [x] 所有 Must Requirement 已通過
- [x] 無未接受的 Critical／High Defect
- [x] 測試證據已保存
