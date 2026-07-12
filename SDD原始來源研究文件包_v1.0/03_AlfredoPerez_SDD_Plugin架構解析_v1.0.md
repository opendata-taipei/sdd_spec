# alfredoperez/sdd Plugin 架構解析

> 版本：1.0  
> 文件性質：原始來源摘要、分析與公司導入參考  
> 檢索日期：2026-07-12

> 本文件是摘要與分析，不是原文重製或官方文件。

## 主流程

specify → plan → tasks → implement，支援 auto、resume、pause 與 status。

## 核心架構

- Skills
- Templates
- Feature Artifacts
- State
- Configuration

## 治理演進

- Living Specs
- Delta Sync
- Drift
- ADR
- Hooks
- Parallel Tasks

## 公司採用

- 增加風險模型
- 狀態 Schema 驗證
- 建立跨 AI Adapter
- 人工 Gate 不可省略

## 參考來源

- Alfredo Perez，[alfredoperez/sdd](https://github.com/alfredoperez/sdd)，Repository；v1.0.0 於 2026-03-08，Changelog 最新記錄 v1.24.0（2026-05-23）。