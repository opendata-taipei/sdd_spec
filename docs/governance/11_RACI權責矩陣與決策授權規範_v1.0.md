# SDD-GOV-011｜RACI 權責矩陣與決策授權規範

> 文件狀態：草案（Draft）  
> 版本：1.0  
> 文件擁有者：[公司名稱／部門]

## 核心規則

- 每項活動只能有一個 Accountable。
- AI／Agent 不得擔任 A、風險接受者或上線核准者。
- L3／L4 必須分離實作、技術核准與生產核准。

## 標準角色

Business Sponsor、Product Owner、Spec Owner、Solution Architect、Tech Lead、Developer、QA、Security、Data Owner、SRE／Release、SDD Process Owner、AI／Automation。

## 生命週期

Intake → Proposal → Requirements → Design／ADR → Tasks → Implement → Review／Test → Release → Drift／Living Spec → Closure。

## 交接與升級

所有 A 指定代理人；交接須包含權威規格、執行狀態、風險與下一 Gate；衝突依 PO／Architect／Security／Change Authority 路徑升級。
