# CHG-2026-003 Requirements

## Functional Requirements

### REQ-ROLE-MAP-001

- Statement：WHEN Gate Approval workflow 解析核准者資格 THEN 系統 SHALL 只從受保護 runtime input 載入 actor／role mapping，不得從公開 repository 取得真實 mapping 或使用不安全 fallback。
- Priority：Must
- Source：FEAT-002、CHG-2026-003 G1
- Acceptance Criteria：
  - AC-001：protected mapping contract 為 UTF-8 JSON object，exact top-level keys 為 `schema_version` 與 `actors`；初版 version 為 `1.0`，actor keys 為 1～20 位不以零開頭的十進位 GitHub actor IDs，最多 1000 actors；每個 actor 對應非空、無重複且只取自 `enterprise-policy.json` allowed roles 的陣列。
  - AC-002：mapping 原始內容上限 32 KiB；JSON 無效、duplicate object key、schema／版本不符、額外欄位、actor key 格式錯誤、未知／duplicate role、actor 數量或 bytes 超限時回傳非 0。
  - AC-003：Approval workflow 缺少 protected mapping 時 fail closed，且不得 fallback 至公開 `config/github-role-map.json`；公開檔持續只含 placeholder。
  - AC-004：actor lookup 以可信 OIDC numeric actor ID 為輸入，不以 display login、Email 或可變名稱作為授權主鍵。

### REQ-GATE-RESOLVE-001

- Statement：WHEN 可信 actor 對指定 Gate 請求核准 THEN resolver SHALL 只在該 actor 恰有一個符合 Gate policy 的 eligible role 時輸出 role。
- Priority：Must
- Source：FEAT-002、`config/enterprise-policy.json`
- Acceptance Criteria：
  - AC-005：actor 不存在、Gate 未知、零個 eligible role 或多個 eligible roles 時回傳非 0，stdout 不輸出 role。
  - AC-006：成功 stdout 只能包含單一 canonical role 與換行；stderr／diagnostic 不得包含 mapping 原文或其他 actors。
  - AC-007：role eligibility 必須直接由當前 `enterprise-policy.json` 的 `gate_policy` 推導，不得由 workflow input 自行宣告。

### REQ-PRIVATE-ACTOR-001

- Statement：WHEN workflow 建立公開可保存的 Approval record THEN 系統 SHALL 將可信 OIDC actor ID 轉換為 repository-scoped、不可由公開資料直接反查的 pseudonymous actor reference。
- Priority：Must
- Source：FEAT-002 Privacy Boundary
- Acceptance Criteria：
  - AC-008：pseudonym 使用 HMAC-SHA-256，由嚴格 Base64 解碼為恰好 32 bytes 的受保護 pepper、固定 domain separator、length-delimited repository ID 與 numeric actor ID 決定；輸出格式版本化且不截短 digest。
  - AC-009：pepper 缺少／非 canonical Base64／解碼長度不等於 32 bytes、actor ID 非預期格式、repository ID 缺失時 fail closed；不得使用未加密 SHA-256、login 或 numeric actor ID 作 fallback。
  - AC-010：相同 repository／actor／pepper 產生相同 pseudonym；不同 repository、actor 或 pepper 產生不同 pseudonym。
  - AC-011：Approval 的 `actor_id` 與縮減 `identity_claim` 不得包含 GitHub login、Email、raw numeric actor ID、原始 OIDC `sub`／`jti` 或完整 JWT。

### REQ-GATE-WORKFLOW-001

- Statement：WHEN 受保護 GitHub Environment 執行 Gate workflow THEN 系統 SHALL 驗證 OIDC context、解析唯一 role、建立 commit-bound Approval artifact，並只輸出最小必要資料。
- Priority：Must
- Source：FEAT-002、Approval Schema
- Acceptance Criteria：
  - AC-012：workflow 驗證 issuer、audience、repository ID、actor ID、workflow reference 與目前 GitHub context 一致，再建立 Approval。
  - AC-013：Approval 必須符合 `approval.schema.json`，`identity_provider=github-oidc`、綁定觸發 workflow 的完整 40 字元 commit SHA，並引用已存在 Evidence IDs。
  - AC-014：protected mapping 與 pepper 只對必要 steps 可見；workflow 不 echo、不加入 `$GITHUB_OUTPUT`、不保存至 artifact。
  - AC-015：原始 OIDC token／暫存檔在 success、failure 與 cancellation cleanup 後均不得成為 artifact；Approval artifact path 只包含本次產生的單一 Approval JSON。
  - AC-016：Environment reviewer、branch protection、CODEOWNERS 與 Change Manager 合併仍是 Human controls；workflow 不得自動合併 Approval。

### REQ-STATE-REMEDIATION-001

- Statement：WHEN CHG-2026-002 的正式 Approvals 已經 review 並合併 THEN 系統 SHALL 以 append-only、當下時間的 remediation events 依合法順序同步 Change State，不得回填虛假歷史。
- Priority：Must
- Source：FEAT-002 Pilot Outcome
- Acceptance Criteria：
  - AC-017：G1～G4 Approvals 必須各自符合當前 policy、role、Evidence、identity provider 與 commit binding；缺少任一 Gate 時不得跨越對應 transition。
  - AC-018：每次 transition 保留原 event chain、使用實際執行時間，並以 payload／evidence 註明 retrospective governance remediation；不得修改既有 event 或 backdate。
  - AC-019：同步後 `reduce_state.py --check`、Enterprise validator 與 event-chain tests 全部通過，且 Feature／Change 文件明確區分實作時間與治理 remediation 時間。
  - AC-020：G5、G6、G7 仍依正常 policy 與職責分離執行，不因 remediation 自動核准或降級。

## Traceability

| Requirement | Design | Task | Test | Status |
|---|---|---|---|---|
| REQ-ROLE-MAP-001 | DES-ROLE-001 | TASK-001 | TEST-ROLE-001, TEST-ROLE-002 | Approved |
| REQ-GATE-RESOLVE-001 | DES-ROLE-001 | TASK-001 | TEST-ROLE-003 | Approved |
| REQ-PRIVATE-ACTOR-001 | DES-IDENTITY-001 | TASK-002 | TEST-IDENTITY-001, TEST-IDENTITY-002 | Approved |
| REQ-GATE-WORKFLOW-001 | DES-WORKFLOW-001 | TASK-003 | TEST-WORKFLOW-001, TEST-WORKFLOW-002 | Approved |
| REQ-STATE-REMEDIATION-001 | DES-REMEDIATION-001 | TASK-005 | TEST-REMEDIATION-001 | Approved |
| NFR-PERF-003 | DES-ROLE-001 | TASK-001 | TEST-PERF-001 | Approved |
| SEC-IDENTITY-002 | DES-IDENTITY-001, DES-WORKFLOW-001 | TASK-002, TASK-003 | TEST-IDENTITY-002, TEST-SECURITY-001 | Approved |
| SEC-PRIVACY-002 | DES-WORKFLOW-001 | TASK-003 | TEST-PRIVACY-001 | Approved |
| OPS-REL-003 | DES-WORKFLOW-001, DES-REMEDIATION-001 | TASK-003, TASK-005 | TEST-WORKFLOW-002, TEST-REMEDIATION-001 | Approved |
