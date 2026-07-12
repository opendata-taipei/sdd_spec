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

### REQ-IDENTITY-PRIVACY-001

- Statement：WHEN Starter Kit 以公開範本發布 THEN 系統 SHALL 僅保存虛構 actor 或 placeholder，且 SHALL 將真實 GitHub login 與角色映射留在私有部署設定。
- Priority：Must
- Source：Security Review
- Acceptance Criteria：
  - AC-004：公開的 `github-role-map.json` 不包含真實 login、Email、Token 或完整 OIDC claims。
  - AC-005：治理文件說明真實 mapping 的私有注入、CODEOWNERS 保護與 IAM 同步責任。
  - AC-006：正式 Approval 僅保存縮減後的必要 claims、commit SHA 與 Evidence references。

## Traceability

| Requirement | Design | Task | Test | Status |
|---|---|---|---|---|
| REQ-MANIFEST-001 | DES-001 | TASK-001 | TEST-MANIFEST-001, TEST-MANIFEST-002 | Draft |
| REQ-IDENTITY-PRIVACY-001 | DES-003 | TASK-005 | TEST-IDENTITY-001 | Draft |
