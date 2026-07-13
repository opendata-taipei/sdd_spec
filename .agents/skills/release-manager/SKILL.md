---
name: release-manager
description: 規劃或執行版本發布、部署檢查、監控與回滾時使用。
---

# Skill：發布與回滾管理

## Purpose

確認 Release Readiness、Deployment、Migration、Monitoring、Rollback 與 Go／No-Go 證據。

## Authoritative Inputs

- Release Plan
- Test Evidence
- Operations Baseline

## Required Outputs

- Go/No-Go Pack
- Runbook
- Post-release Checklist

## Operating Rules

1. 先確認 Change ID、Risk Level、目前 State 與適用 Gate。
2. 必須引用 Requirement、Task、ADR 或 Policy ID；不得只引用聊天內容。
3. 不得自行核准風險、Release、Security Exception 或 Scope Expansion。
4. 發現衝突、缺失或不可逆風險時，輸出 `HUMAN_DECISION_REQUIRED`。
5. 所有輸出必須保存於 Repository，可被不同 AI 或人員接手。

## Completion Criteria

- 輸出符合對應 Template。
- 假設、風險、未解決問題與證據已列出。
- Execution State 已更新。
- 下一步及下一個 Gate 明確。
