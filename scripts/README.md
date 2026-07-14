# Scripts

## Enterprise controls

- `validate_enterprise.py`：檢查 Gate Approval、角色、Evidence 引用與 hash、Manifest/State 一致性。
- `run_evals.py`：檢查供應商中立的 Agent assurance baseline。
- `transition_state.py`：依狀態機移轉，並在關鍵階段強制檢查 Gate Approval；須提供 `--actor-role`。
- `create_approval.py`：以 `--from-env` 從 validated dispatch inputs 與 `SDD_ACTOR_ID`、`SDD_ACTOR_ROLE`、`SDD_IDENTITY_PROVIDER`、`SDD_IDENTITY_CLAIM`、`SDD_COMMIT_SHA` 建立 atomic、single-file 正式核准；不覆寫既有 target。
- `run_agent_evals.py`：透過 JSONL adapter protocol 實際執行跨供應商 Agent 治理評測。
- `init_event_store.py`／`append_event.py`／`reduce_state.py`：初始化、追加及驗證 hash-chained Change Event Store。
- `gate_identity.py`：提供 strict protected role-map、policy resolver、OIDC context、HMAC pseudonym 與 reduced-claim contracts。
- `prepare_gate_identity.py`：驗證 GitHub OIDC response 與 runner context，向 `GITHUB_OUTPUT` 寫入最小安全 identity outputs。
- `resolve_github_role.py`：只從 `SDD_GITHUB_ROLE_MAP_JSON` 受保護 input，以 numeric `--actor-id` 解析 Gate 核准角色；沒有 public-map fallback。
- `runtime_audit.py`／`validate_runtime_audit.py`：建立並驗證 Agent Run、Context、Tool、Guardrail 與輸出稽核包。
- `run_to_evidence.py`：將完成的 Agent Run 提升為可供 Gate 引用的 Evidence。
- `build_kit_manifest.py`：重建或以 `--check` 驗證套件版本與完整檔案清單。
- `package_starter_kit.py`：建立 deterministic ZIP 與外部 sidecars，或先 fail-closed 驗證再安全解壓。

- `bootstrap_change.py`：從 `_template` 建立新 Change。
- `validate_sdd.py`：檢查必要文件、State、Requirement／Task／Test 基本追溯。
- `portability_check.py`：檢查正式規格是否依賴聊天記錄、私有記憶或工具專用命令。
- `drift_check.py`：比較 Git Diff 與 `manifest.yaml` 的 `declared_files`。
- `build_context_pack.py`：建立可供不同 AI／人員載入的工具中立 Context Pack。
- `transition_state.py`：依合法狀態機更新 Change State 並記錄 Actor／Evidence。

這些腳本是最低限度的 Starter Validation，不取代正式 Schema Validator、SAST、DAST、Contract Test 或公司既有 CI/CD Controls。
