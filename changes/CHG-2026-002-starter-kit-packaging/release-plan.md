# CHG-2026-002 Release & Rollback Plan

## Release Strategy

- Strategy：Versioned artifact release（v1.5.0）
- Window：G5 verification 與 release commit CI 成功後
- Owner：Starter Kit Maintainer

## Pre-release Checklist

- [ ] Build／Test／Security Gate 通過
- [ ] Migration 已演練
- [ ] Monitoring／Alert 已啟用
- [ ] Rollback Trigger 已確認

## Deployment Runbook

1. 以 package CLI 從 release commit 建立 ZIP、metadata 與 SHA-256。
2. 在乾淨 temporary directory 執行 safe verify 與 governance round trip。
3. 由 GitHub Actions 保存 Windows／Linux artifacts 與 checksum comparison report。
4. 更新 Feature status、Changelog、Manifest 與 release notes。
5. 建立並推送 `v1.5.0` annotated tag。

## Rollback Triggers

- Windows／Linux checksum 不一致。
- Archive entry set 與 Manifest 不一致。
- 任一路徑安全或敏感資料測試失敗。
- 無 `.git` round-trip governance validation 失敗。

## Rollback Procedure

1. 不發布或刪除失敗的 draft artifact。
2. Revert package workflow／CLI release commit，不回退 v1.4.1 核心治理能力。
3. 保存 failure evidence 並重新開啟 CHG-2026-002 remediation task。

## Post-release Verification

- Smoke Test：下載公開 ZIP 與 metadata，重新計算 SHA-256、safe verify、解壓後執行核心 validators
- Observation Window：至少一輪 Windows 與 Linux Actions 均成功
