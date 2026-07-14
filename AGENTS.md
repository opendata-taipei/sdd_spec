# AGENTS.md

本檔是此 Repository 的根層 Agent 執行規則，適用於整個專案。若子目錄另有 `AGENTS.override.md` 或 `AGENTS.md`，以更接近工作目錄的規則補充或覆寫本檔。

## Mission

這是 SDD／Agentic Company Starter Kit。所有 Agent 的任務是依可追溯規格完成變更，保留 Human Gate、Evidence、Rollback 與跨工具接手機制，而不是只讓程式或測試暫時通過。

## Authoritative Sources

遇到衝突時依下列順序判斷；不得用聊天記憶取代 Repository 內容：

1. 公司政策、法律與使用者當前明確指示。
2. `constitution/project-constitution.md` 與 `constitution/ai-execution-contract.md`。
3. `specs/living/` 與 `specs/features/`。
4. `changes/<Change ID>/` 中已核准的 Proposal、Requirements、NFR、Design、Tasks 與 Test Plan。
5. `adr/`、schemas、程式碼、自動化測試及 Git diff。
6. `.agents/skills/`、`agents/` 與 `adapters/` 等執行輔助層。

程式碼與規格不一致時，先回報 drift；不得自行假定任一方正確。

## Before Editing

1. 讀取本檔、兩份 Constitution、相關 Feature 與 Change 文件。
2. 確認 `change_id`、risk level、current phase、current task、requirements in scope 與下一個合法 Gate。
3. 檢查 `git status --short`；保留使用者既有變更，不重設、不覆寫無關檔案。
4. 確認預計修改的檔案已列於 Change `manifest.yaml` 的 `declared_files`；新增或刪除檔案也必須受管。
5. 列出必要假設、風險與驗證方式。規格衝突、範圍擴張、不可逆操作或 residual risk 必須先取得 Human Decision。

若沒有合適 Change，先判斷工作是否達到 Standard／Major／Critical；達到時使用唯一 Change ID 建立完整 Change，不得把重大功能藏在未追蹤的小修改中。

## Human Gates and Identity

- Agent 可以整理審查資料與建立可驗證 Evidence，但不得自行核准 G1～G7、Release、Security Exception 或 Risk Acceptance。
- 對話中的 Human Decision 可作為工作授權，但不得偽造 `approval/*.json`、OIDC claim、GitHub login、commit signature 或企業角色。
- 正式 Approval 只能依 `config/enterprise-policy.json`，透過受信任 identity provider 與實際 commit SHA 建立。
- 不得將真實 Email、Token、Cookie、Password、GitHub login 或私有 IAM mapping 寫入公開 Starter Kit；使用 placeholder 或私有 deployment overlay。
- 已被 Gate 引用的 Requirement、Design 與 Evidence 視為不可變。需要修正時新增 addendum／superseding evidence 並重新送審，不得偷偷改寫歷史。

## Change Lifecycle

遵循 `config/enterprise-policy.json` 與狀態機：

```text
Proposal → G1 → Requirements → G2 → Design → G3
→ Ready for Implementation → G4 → Implementing
→ Verification → G5 → Release Ready → G6
→ Monitoring / Closure → G7
```

- Requirement 必須有 ID、Acceptance Criteria 與 Test／Evidence mapping。
- Task 必須連回 Requirement 或明確治理工作。
- 實作不得超出已核准 Design；必要變更先更新規格並取得適當 Gate。
- 狀態與 Gate 是 Event／Approval 推導結果；不要手工捏造 `state.json` 或在 Manifest 儲存衍生狀態。
- Evidence 必須可重現、綁定 artifact hash，並通過 schema 與本地 hash 驗證。

## Repository Map

- `constitution/`：永久原則與 AI execution contract。
- `specs/living/`：目前真實狀態；`specs/features/`：跨版本能力追蹤。
- `changes/`：每次變更的規格、state、event、approval 與 evidence。
- `docs/governance/`：公司級流程與操作制度。
- `.agents/skills/`：repo-scoped、可直接發現的 `SKILL.md` workflows。
- `agents/`：角色型 Agent、orchestrator、狀態與 handoff contract。
- `schemas/`、`config/`：機器可驗證契約與企業政策。
- `scripts/`、`tests/`、`evals/`：控制腳本、回歸測試與 agent assurance。
- `adapters/`：供應商／工具薄層；不得成為正式規格唯一來源。
- `KIT_MANIFEST.json`：公開 Starter Kit 的唯一發布 allowlist。

`.codex/`、`.skills/`、`.venv/`、`dist/`、runtime reports、研究附件與 private overlays 不得誤入發布包。

## Editing Rules

- 優先做最小、可回滾且符合既有架構的修改；不要順手重構無關內容。
- Python 控制腳本維持 Python 3.12+ 相容。封裝 runtime 只用 standard library；治理 validator 的鎖定依賴在 `requirements-governance.txt`。
- 公開資料契約以 JSON Schema Draft 2020-12 表示，預設拒絕未定義欄位。
- 所有公開介面、schema、artifact format 與 migration 必須版本化並具 rollback／forward-fix 說明。
- 文字檔維持 UTF-8 與 LF；遵守 `.gitattributes`。不得破壞 Windows／Linux deterministic package hash。
- 不跟隨或封裝 symlink／junction；不得放寬 path traversal、size limit、secret redaction 或 fail-closed controls。
- 不使用破壞性 Git／filesystem 指令處理使用者變更。不得使用 `git reset --hard`、強制 checkout 或未核准的 recursive delete。

## Skills

- 任務明確符合 `.agents/skills/<name>/SKILL.md` 時，先完整讀取該 Skill，再依其 progressive-disclosure 規則載入必要 references／scripts。
- `SKILL.md` 必須有 `name` 與清楚的 `description` frontmatter；正式 repo skills 只放在 `.agents/skills/`。
- 根目錄 `.skills/` 是本機工具資產，不是權威來源，也不列入 Kit Manifest。
- Skill、Prompt 或 Adapter 只能協助執行，不能覆蓋 Constitution、Requirement 或 Human Gate。

## Validation

安裝治理依賴：

```bash
python -m pip install -r requirements-governance.txt
```

每次修改至少執行與風險相稱的檢查。提交前的完整基線為：

```bash
python scripts/validate_sdd.py
python scripts/validate_enterprise.py
python -m unittest discover -s tests -v
python scripts/run_evals.py
python scripts/run_agent_evals.py
python scripts/validate_runtime_audit.py
python scripts/build_kit_manifest.py --check
python scripts/portability_check.py
python -m compileall -q scripts evals/adapters tests
python scripts/drift_check.py --change <CHANGE_ID>
```

規則：

- 新增、刪除、移動或改名任何受管檔案後，先執行 `python scripts/build_kit_manifest.py`，再以 `--check` 驗證。
- `--check` 必須保持唯讀；不得以驗證命令偷偷修正檔案。
- 修改 package contract 時另執行 `tests/test_starter_kit_packaging.py`，並完成 build／safe verify／無 `.git` governance round trip。
- 修改 security、identity、approval、event chain 或 evidence 時，必須包含對應 failure-path regression tests。
- 測試失敗時先定位根因；不得刪除測試、放寬 assertion 或降低安全控制來取得綠燈。
- GitHub Actions 的 Windows／Linux package jobs 與 checksum comparison 都成功，才可把跨平台 deterministic outcome 記為 Evidence。

## Packaging

```bash
python scripts/package_starter_kit.py build
python scripts/package_starter_kit.py verify \
  dist/sdd-agentic-starter-kit-1.5.0-dev.zip \
  --destination dist/verified --run-governance
```

- Build 只以 `KIT_MANIFEST.json` 為 allowlist，sidecars 必須在 ZIP 外。
- Verify 必須先完整檢查 checksum、metadata、entry set、path、size 與 hash，再寫入新的 staging／destination。
- 不覆寫既有 destination；失敗不得留下部分解壓內容。
- SHA-256 只表示完整性，不代表 publisher authenticity。

## Completion and Handoff

完成回報必須包含：

- Change／Feature、Requirement 與 Task IDs。
- 實際修改檔案與重要設計決策。
- 執行過的測試、結果與未執行項目的理由。
- 已知風險、blocker、rollback 與下一個合法 Gate。
- Commit／CI／Evidence 連結；不得宣稱未觀察到的外部狀態。

未通過所需 Human Gate、CI、Drift、Living Spec sync 與 Evidence 保存前，只能說「已實作」或「待驗證」，不得宣告 Change／Release 完成。
