# CHG-2026-001 Release & Rollback Plan

## Release Strategy

- Strategy：Versioned documentation/tooling release
- Window：合併 v1.4.1 release commit 後立即生效
- Owner：Starter Kit Maintainer

## Pre-release Checklist

- [x] Build／Test／Security Gate 通過
- [x] Repo-root migration 已由 Windows 本機與 Linux GitHub Actions 驗證
- [x] GitHub Actions 提供持續監控
- [x] Rollback Trigger 已確認

## Deployment Runbook

1. 更新 Changelog、README 與 Manifest 版本為 1.4.1。
2. 執行完整本機治理與測試檢查。
3. Push release commit，確認 `SDD Quality Gates` 成功。
4. 建立 `v1.4.1` tag（如採用 Git tag 發布）。

## Rollback Triggers

- Manifest Gate 對未變更的發布內容產生誤判。
- Windows 或 Linux 任一 runner 產生不同 Manifest 清單。
- CI check 修改工作區或執行時間超過 5 秒。

## Rollback Procedure

1. Revert v1.4.1 release commit 與 Manifest Gate implementation commit。
2. 重跑原有 SDD、Enterprise、Eval 與 Portability checks。
3. 保存失敗 run URL 與 rollback Evidence。

## Post-release Verification

- Smoke Test：`python scripts/build_kit_manifest.py --check` 與完整 GitHub Actions workflow
- Observation Window：至少一個 main branch 成功 run
