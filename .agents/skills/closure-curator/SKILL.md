---
name: closure-curator
description: 完成變更結案、Living Spec 同步、證據歸檔與知識沉澱時使用。
---

# Skill：結案與知識沉澱

## Purpose

同步 Living Specs、ADR、Runbook，完成 Closure Report、Lessons Learned 與可攜性交接驗證。

## Authoritative Inputs

- Completed Change
- Drift Report
- Release Evidence

## Required Outputs

- closure-report.md
- Living Spec Updates
- Knowledge Archive

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
