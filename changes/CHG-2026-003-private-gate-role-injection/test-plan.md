# CHG-2026-003 Test Plan

## Entry Criteria

- [x] Requirement 與 Design 已核准
- [ ] Protected GitHub Environment 與 private data 可用；local synthetic fixtures 已可用

## Test Cases

| Test ID | Requirement | Level | Scenario | Expected | Evidence |
|---|---|---|---|---|---|
| TEST-ROLE-001 | REQ-ROLE-MAP-001 | Unit | 合法 protected JSON、allowed roles 與 numeric actor IDs | parse 成 canonical in-memory mapping，不輸出原文 | unittest output |
| TEST-ROLE-002 | REQ-ROLE-MAP-001, SEC-IDENTITY-002 | Security | missing／oversize／invalid JSON、duplicate key、extra property、invalid actor ID、unknown／duplicate role | 全部 fail closed，stdout 無 mapping | unittest output |
| TEST-ROLE-003 | REQ-GATE-RESOLVE-001 | Unit | actor missing、unknown Gate、零個／多個 eligible role 與唯一 role | 只有唯一 eligible role 成功 | unittest output |
| TEST-IDENTITY-001 | REQ-PRIVATE-ACTOR-001 | Unit | 相同／不同 repo、actor、pepper 的 HMAC fixtures | deterministic、domain-separated、full digest pseudonym | unittest output |
| TEST-IDENTITY-002 | REQ-PRIVATE-ACTOR-001, SEC-IDENTITY-002 | Security | missing／non-canonical Base64／非 32-byte pepper、invalid actor／repo，以及禁止 raw hash fallback | 全部 fail closed；無 raw identifier | security test report |
| TEST-WORKFLOW-001 | REQ-GATE-WORKFLOW-001 | Integration | protected Environment、合法 OIDC、mapping、pepper、Evidence 與 commit | 只產生單一 schema-valid Approval artifact | GitHub Actions artifact／run URL |
| TEST-WORKFLOW-002 | REQ-GATE-WORKFLOW-001, OPS-REL-003 | Failure | mapping／pepper／OIDC／Evidence 缺失、shell metacharacter input、job cancellation、existing target | 非 0、cleanup 完成、不覆寫、無 partial Approval artifact | Actions negative test log |
| TEST-SECURITY-001 | SEC-IDENTITY-002 | Security | spoofed actor／repository／audience／workflow ref、expired token、role/input injection、invalid actor reference／claim mismatch | 全部拒絕，0 unauthorized Approval | security test report |
| TEST-PRIVACY-001 | SEC-PRIVACY-002 | Privacy | 掃描 Git diff、package、stdout／stderr、workflow log 與 artifact | 0 login／Email／raw actor ID／mapping／pepper／JWT／Token finding | privacy scan report |
| TEST-PERF-001 | NFR-PERF-003 | Performance | 32 KiB mapping fixture 重複 100 次 | p95 < 200 ms；process peak RSS < 64 MiB | benchmark report |
| TEST-REMEDIATION-001 | REQ-STATE-REMEDIATION-001, OPS-REL-003 | Integration | CHG-2026-003 bootstrap 與 CHG-2026-002 正式 G1～G4 Approval 合併後順序 transition | 每 Gate fail closed；event chain append-only、current timestamp、remediation reason、state projection 與 Enterprise validation通過 | repository events／CI log |

## Exit Criteria

- [ ] 所有 Must Requirement 已通過
- [ ] 無未接受的 Critical／High Defect
- [ ] 測試證據已保存

## Implementation Verification Status

| Scope | Status | Notes |
|---|---|---|
| TEST-ROLE-001～003 | Pass | strict parser、failure paths、unique policy role 與 stdout contract |
| TEST-IDENTITY-001～002 | Pass | HMAC domain separation、canonical pepper、numeric IDs、exact reduced claim |
| TEST-WORKFLOW-001 | Partial | local synthetic end-to-end pass；real protected Environment artifact 尚待 Human-controlled run |
| TEST-WORKFLOW-002 | Partial | local missing／malicious／existing-target paths pass；real cancellation log 尚待 Environment run |
| TEST-SECURITY-001 | Pass locally | issuer／audience／repository／actor／workflow_ref／run／time／claim mismatch 拒絕 |
| TEST-PRIVACY-001 | Pass locally | outputs／synthetic artifact／workflow／Kit 未保存 injected mapping、pepper、JWT 或 raw actor ID；real Actions log 待查 |
| TEST-PERF-001 | Pass | 32 KiB fixture ×100，p95 與 peak RSS assertions 通過 |
| TEST-REMEDIATION-001 | Partial | reducer reason projection pass；正式 merged Approvals 與 CHG-2026-002 pilot 尚待 TASK-005 |

Cross-platform Quality Gates run `29351982743` 已通過 Linux／Windows package round-trip 與 checksum comparison；此結果不改變 protected Environment tests 的 Partial 狀態。
