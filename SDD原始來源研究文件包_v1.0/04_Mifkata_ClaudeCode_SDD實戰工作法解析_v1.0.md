# Mifkata：Claude Code SDD 實戰工作法解析

> 版本：1.0  
> 文件性質：原始來源摘要、分析與公司導入參考  
> 檢索日期：2026-07-12

> 本文件是摘要與分析，不是原文重製或官方文件。

## 核心問題

AI 對話壓縮與人員遺忘使 Context 流失，Spec 用來持久化可重載工程知識。

## 命令

- spec-create
- spec-compact
- spec-apply
- spec-verify
- spec-update
- spec-refactor
- test-create

## 主要風險

- 過度壓縮不利人類審核
- Code → Spec 可能把錯誤正式化
- 缺少正式治理 Gate

## 公司建議

- 正式 Spec + Agent Summary 雙層
- Verify 納入 Gate
- Sync 需決策證據
- Refactor 需回歸測試

## 參考來源

- Mifkata，[Claude Code: Spec-Driven Development (SDD)](https://mifkata.com/blog/2026/01/claude-code-spec-driven-development/)，2026-01-08；更新 2026-02-22。