# SDD-001 規格驅動開發（SDD）管理政策

> 文件狀態：草案（Draft）  
> 版本：1.0  
> 文件擁有者：[公司名稱／部門]

## 核心政策

規格是可攜、可審核的權威來源；AI 是可替換的執行者。需求、設計、任務、程式碼、測試、發布與 Living Specs 必須可追溯。

## 最低流程

Classification → Proposal → Requirements → Design → Tasks → Implement → Verification → Drift Check → Release → Living Spec Sync／Archive。

## AI 可替換要求

- 規範性文件不得依賴單一模型的隱藏記憶。
- 特定工具指令放入 Adapter 層。
- 不同 AI 必須接受同一 Requirements、Tests 與人工 Gate。
