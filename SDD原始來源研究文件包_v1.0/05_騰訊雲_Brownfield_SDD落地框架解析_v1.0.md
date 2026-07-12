# 騰訊雲：Brownfield SDD 落地框架解析

> 版本：1.0  
> 文件性質：原始來源摘要、分析與公司導入參考  
> 檢索日期：2026-07-12

> 本文件是摘要與分析，不是原文重製或官方文件。

## 場景

存量程式碼邊界、測試與隱性知識不足，直接使用 AI 容易造成連鎖回歸。

## 工具分工

- Claude Code：執行環境
- OpenSpec：變更規格生命週期
- Superpowers：TDD 與工程紀律
- Constitution：永久規則

## 四階段

- 建立 Constitution
- 需求規格化
- 方案與任務 Gate
- 逐任務實作、驗證、歸檔

## 公司建議

- 先讀碼再寫 Spec
- Plan Gate 明確判定
- 全量回歸
- 工具鎖版與 Pilot

## 參考來源

- GimaCode／騰訊雲開發者社群，[規格驅動開發（SDD）：如何用 Claude Code + OpenSpec + Superpowers 在歷史專案中落地](https://cloud.tencent.com/developer/article/2670128)，2026-05-18（頁面標示修改日期）。