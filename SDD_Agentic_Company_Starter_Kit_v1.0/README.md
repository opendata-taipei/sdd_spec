# SDD／Agentic 公司級 Starter Kit v1.0

這是一套可直接納入公司 Git Repository 的 **Spec-Driven Development（SDD）與 Agentic Engineering** 基礎架構。

核心原則：

1. **規格是權威來源，AI 是可替換執行者。**
2. 所有人員與 AI 必須依相同 Requirement、Design、Task、Test 與 Quality Gate 工作。
3. 工具專用 Prompt、Skill、Command 與 Adapter 不得取代正式規格。
4. AI 不得擔任最終核准者、風險接受者、資安例外核准者或 Production Release Approver。
5. 未通過 Human Gate、測試、Drift Check 與 Living Spec Sync，不得宣告完成。

## 內容

- `docs/governance/`：公司級 01～16 SDD 制度文件（Markdown）。
- `constitution/`：每個專案永久有效的規範與 AI 執行契約。
- `specs/living/`：目前系統真實狀態與長期規格。
- `changes/`：每次變更的 Proposal、Requirements、Design、Tasks、Test、Release 與 Closure。
- `skills/`：工具中立、可被不同 Agent 使用的技能契約。
- `agents/`：角色型 Agent 定義、Orchestrator、狀態機與交接規範。
- `schemas/`：Execution State、Requirement、Task、Agent Output 的 JSON Schema。
- `scripts/`：建立 Change、驗證規格、Drift Check、AI 可攜性檢查。
- `.github/`：PR Template、CODEOWNERS 範例與 CI Quality Gate。
- `adapters/`：把工具中立規格接到不同 AI／IDE／CLI 的薄層範例。

## 快速開始

```bash
# 1. 建立新的變更目錄
python scripts/bootstrap_change.py CHG-2026-001 add-account-lockout

# 2. 編輯 proposal、requirements、design、tasks 與 test-plan

# 3. 驗證文件完整性與追溯關係
python scripts/validate_sdd.py

# 4. 檢查正式規格是否出現工具綁定內容
python scripts/portability_check.py

# 5. 建立跨 AI／人員可重載的 Context Pack
python scripts/build_context_pack.py --change CHG-2026-001

# 6. 在 Git Repository 中檢查未規格化變更
python scripts/drift_check.py --change CHG-2026-001
```

## 推薦執行順序

```text
Project Constitution
  ↓
Living Specs
  ↓
Change Proposal
  ↓ Human Gate G1
Requirements / NFR
  ↓ Human Gate G2
Technical Design / ADR
  ↓ Human Gate G3
Tasks / Test Plan
  ↓ Definition of Ready
Implementation
  ↓ Code Review / Automated Tests / Security
Verification
  ↓ Drift Check / Living Spec Sync
Release & Rollback
  ↓ Human Go / No-Go
Monitoring / Closure / Knowledge Archive
```

## AI 可替換性

任何 AI、IDE Agent 或 CLI Agent，應只依以下內容恢復工作：

- `constitution/`
- `specs/living/`
- `changes/<Change ID>/`
- Git Diff、Test Result、Execution State

不得要求取得原 AI 的聊天紀錄或私有記憶才可繼續。

## Enterprise Control Plane v1.3

本套件提供供應商中立的企業控制層：

- `config/enterprise-policy.json`：Gate、角色、核准數與狀態前置條件。
- `schemas/evidence.schema.json`、`approval.schema.json`、`agent-run.schema.json`：證據、核准及 Agent 稽核契約。
- `scripts/validate_enterprise.py`：核准、Evidence hash、Manifest/State 一致性檢查。
- `evals/`：Agent 治理與安全回歸基線。

完整說明見 `docs/governance/17_Enterprise_Agent_Control_Plane_v1.1.md`。

v1.3 另加入 GitHub OIDC Approval、append-only Event Store，以及 OpenAI/Claude Eval Adapters；操作方式見 `docs/governance/18_Enterprise_Pilot_Integration_v1.3.md`。

v1.4 加入 Agent Runtime Audit、敏感資料遮罩與 Run-to-Evidence promotion；操作方式見 `docs/governance/19_Agent_Runtime_Audit_v1.4.md`。

## 初次導入建議

先從一個 L1～L2 風險的內部功能進行 Pilot，完成一整個 Change Lifecycle，再決定是否擴展至 Production Critical 系統。
