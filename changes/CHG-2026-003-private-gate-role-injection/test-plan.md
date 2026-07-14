# CHG-2026-003 Test Plan

## Entry Criteria

- [ ] Requirement 與 Design 已核准
- [ ] Test Environment 與 Data 可用

## Test Cases

| Test ID | Requirement | Level | Scenario | Expected | Evidence |
|---|---|---|---|---|---|
| TEST-ROLE-001 | REQ-ROLE-MAP-001 | Unit | 合法 protected JSON、allowed roles 與 numeric actor IDs | parse 成 canonical in-memory mapping，不輸出原文 | unittest output |
| TEST-ROLE-002 | REQ-ROLE-MAP-001, SEC-IDENTITY-002 | Security | missing／oversize／invalid JSON、duplicate key、extra property、invalid actor ID、unknown／duplicate role | 全部 fail closed，stdout 無 mapping | unittest output |
| TEST-ROLE-003 | REQ-GATE-RESOLVE-001 | Unit | actor missing、unknown Gate、零個／多個 eligible role 與唯一 role | 只有唯一 eligible role 成功 | unittest output |
| TEST-IDENTITY-001 | REQ-PRIVATE-ACTOR-001 | Unit | 相同／不同 repo、actor、pepper 的 HMAC fixtures | deterministic、domain-separated、full digest pseudonym | unittest output |
| TEST-IDENTITY-002 | REQ-PRIVATE-ACTOR-001, SEC-IDENTITY-002 | Security | missing／non-canonical Base64／非 32-byte pepper、invalid actor／repo，以及禁止 raw hash fallback | 全部 fail closed；無 raw identifier | security test report |
| TEST-WORKFLOW-001 | REQ-GATE-WORKFLOW-001 | Integration | protected Environment、合法 OIDC、mapping、pepper、Evidence 與 commit | 只產生單一 schema-valid Approval artifact | GitHub Actions artifact／run URL |
| TEST-WORKFLOW-002 | REQ-GATE-WORKFLOW-001, OPS-REL-003 | Failure | mapping／pepper／OIDC／Evidence 缺失、job cancellation | 非 0、cleanup 完成、無 partial Approval artifact | Actions negative test log |
| TEST-SECURITY-001 | SEC-IDENTITY-002 | Security | spoofed actor／repository／audience／workflow ref、role input injection | 全部拒絕，0 unauthorized Approval | security test report |
| TEST-PRIVACY-001 | SEC-PRIVACY-002 | Privacy | 掃描 Git diff、package、stdout／stderr、workflow log 與 artifact | 0 login／Email／raw actor ID／mapping／pepper／JWT／Token finding | privacy scan report |
| TEST-PERF-001 | NFR-PERF-003 | Performance | 32 KiB mapping fixture 重複 100 次 | p95 < 200 ms；process peak RSS < 64 MiB | benchmark report |
| TEST-REMEDIATION-001 | REQ-STATE-REMEDIATION-001, OPS-REL-003 | Integration | CHG-2026-002 正式 G1～G4 Approval 合併後順序 transition | event chain append-only、非 backdate、state projection 與 Enterprise validation 通過 | repository events／CI log |

## Exit Criteria

- [ ] 所有 Must Requirement 已通過
- [ ] 無未接受的 Critical／High Defect
- [ ] 測試證據已保存
