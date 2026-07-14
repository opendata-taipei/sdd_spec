# CHG-2026-003 Change Proposal：Private Gate Role Injection

- Status：Draft
- Risk Level：L2
- Change Owner：Justin
- Product Owner：Justin

## 問題與背景

目前 `SDD Gate Approval` workflow 只從 repository 內的 `config/github-role-map.json` 解析 GitHub actor 與 Gate role。公開 Starter Kit 基於隱私與最小揭露原則，只能保存 placeholder，導致正式 workflow 無法辨識實際核准者；若直接提交真實 login／role mapping，又會公開內部授權關係。

因此 CHG-2026-002 雖已有 G1～G3 review evidence、完整實作與跨平台 CI evidence，仍無法在不洩漏真實 GitHub login 的前提下產生符合 `approval.schema.json`、可信 OIDC 與 commit binding 的正式 Approval records，Event State 也只能維持 DRAFT。

## 目標與成功指標

- Objective：讓 Gate workflow 從受保護的 runtime configuration 解析 actor／role，同時保持公開 repository 零真實身分映射。
- Metric：公開 role map 仍只有 placeholder；合法受保護 mapping 可產生 schema-valid Approval；缺失、格式錯誤、actor 不存在、role 不合 Gate 或多重 eligible role 時全部 fail closed；log、artifact 與 package 不含 mapping、token 或完整 OIDC JWT。

## 範圍

### In Scope

- 定義受保護 GitHub Environment secret／variable 或企業 IAM 產物的 runtime role-map contract。
- `resolve_github_role.py` 支援明確的受保護輸入來源，並驗證 schema、actor、Gate 與唯一 eligible role。
- `sdd-gate-approval.yml` 以最小權限注入 mapping，不將內容寫入 Git、log 或 artifact。
- 補齊 success／failure-path tests、操作 runbook 與公開 Starter Kit placeholder 行為。
- 以 CHG-2026-002 作為 pilot，證明可產生正式 Approval artifact 並依法推進 Event State。

### Out of Scope

- 將真實 GitHub login、Email、Team membership 或 IAM mapping 提交到公開 repository。
- 保存原始 OIDC JWT、GitHub token 或不必要的 claims。
- 自動核准 Gate、繞過 Environment reviewer、CODEOWNERS、branch protection 或職責分離。
- 改變 `enterprise-policy.json` 的 Gate roles、minimum approvals 或 L3／L4 separation-of-duties。
- 自動合併 Approval artifact 或直接修改 production／release state。

## 影響與風險

| 項目 | 影響 | 風險 | 緩解 |
|---|---|---|---|
| Identity privacy | mapping 由 Git 改為 runtime protected input | secret／variable 誤輸出至 log | 不 echo 原文、最小環境範圍、secret scanning 與 artifact inspection test |
| Authorization | role resolver 決定 Gate eligibility | malformed mapping 或 role confusion 造成 privilege escalation | strict schema、Gate allowlist、唯一 eligible role、fail closed |
| Availability | 缺少 protected configuration 時 workflow 失敗 | 初次部署無法核准 | 明確 preflight 與 runbook，不提供不安全 fallback |
| Auditability | Approval 綁定 actor、縮減 OIDC claims 與 commit SHA | artifact 與合併 commit 不一致 | 保留 workflow run URL、commit binding 與 Enterprise validator evidence |
| Pilot recovery | CHG-2026-002 需補走正式狀態 | 歷史狀態與實作時序不一致 | 以 append-only remediation events 說明，不回寫或偽造舊時間點 |

## Gate G1

- [x] Business Problem 已確認
- [x] Scope／Out of Scope 已確認
- [ ] Risk Level 已核准
- [x] Owner 與 Success Metric 已定義
