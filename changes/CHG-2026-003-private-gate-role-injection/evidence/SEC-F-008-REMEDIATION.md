# SEC-F-008 Kit Runtime Exclusion Remediation

- Change：CHG-2026-003
- Feature：FEAT-002
- Requirements：SEC-PRIVACY-002、OPS-REL-003
- Design：Design Addendum 003
- Task：TASK-007
- Test：TEST-KIT-PRIVACY-001
- Produced：2026-07-15T05:02:39Z
- Result：pass

## Finding Reproduction

Mode A negative-run raw logs 位於 Git-ignored top-level `tmp/` 時，修正前 `scripts/build_kit_manifest.py` 會將 10 個 runtime files 加入 `KIT_MANIFEST.json`，造成 `python scripts/build_kit_manifest.py --check` fail closed。未將含 `tmp/` entries 的 Manifest 保留或用於發布。

## Implemented Control

- `scripts/build_kit_manifest.py` 的 exact `IGNORED_TOP_LEVEL` 加入 `tmp`。
- `tests/test_kit_manifest.py` 新增 nested raw-log fixture，驗證 build 與 read-only `--check` 都排除所有 `tmp/` descendants。
- 原 unmanaged public file failure-path test 保持通過；控制沒有放寬其他 repository paths。
- Raw logs 未移動、未刪除、未加入 Git；`git status --ignored` 將其識別為 `!! tmp/`。

## Verification

| Check | Result |
|---|---|
| Targeted Kit Manifest tests | 9/9 pass |
| Full unittest discovery | 43 tests pass |
| `validate_sdd.py` | 0 errors、0 warnings |
| `validate_enterprise.py` | 0 errors、0 warnings |
| Evals／Agent evals | 4 cases pass／4 of 4 pass |
| Runtime audit | 14 runs、0 errors |
| Portability／compileall／drift | pass／pass／PASS，0 unspeced drift |
| Manifest with raw logs present | valid，262 files；0 `tmp/` entry |
| Local package build／safe verify with governance | pass；262 entries、0 `tmp/` entry |
| Verified ZIP SHA-256 | `291c920794197446be212c4e7f0aea58260032d27623b7895e4bdaf78cdb4a46` |
| Verified uncompressed size | 449,340 bytes |

Package runtime output僅位於 ignored `dist/sec-f-008-build` 與 `dist/sec-f-008-verified`，不納入 Repository Evidence 或 Kit。

## Cross-platform CI Verification

- Pull Request：[PR #1](https://github.com/opendata-taipei/sdd_spec/pull/1)
- Quality Gates：[run 29402752423](https://github.com/opendata-taipei/sdd_spec/actions/runs/29402752423)
- Event：`pull_request`
- Head commit：`8e37e80ac47ab52d25bca243d5233944aa802283`
- Started：2026-07-15T08:58:41Z
- Completed：2026-07-15T08:59:40Z
- Conclusion：success

| Job | Result | Evidence |
|---|---|---|
| `validate-sdd` | success | validators、43 tests、evals、runtime audit、Kit Manifest、portability、compileall steps all success |
| `package-round-trip (ubuntu-latest)` | success | deterministic build、safe verify／governance、package upload all success |
| `package-round-trip (windows-latest)` | success | deterministic build、safe verify／governance、package upload all success |
| `compare-package-checksums` | success | `Require identical Windows and Linux archives` success |

GitHub artifact metadata：

- `starter-kit-Linux`：159,461 bytes；artifact digest `sha256:98b1dc4c31e1db4fe4b813e5c5fe9b69751088939029232b170697a110067205`。
- `starter-kit-Windows`：159,461 bytes；artifact digest `sha256:906c6fd340838ab4b8795fea021bd610a57440a5af58b0b5c6f3d6af9152e5b8`。

兩個 GitHub artifact digests 是各自外層 artifact archive 的完整性值；跨平台 Starter Kit archive equality 由 comparison job 的成功結果證明，不將不同的外層 digest誤述為內層 ZIP 不一致。

## Security Disposition

SEC-F-008 required control 已由 regression、current-workspace Manifest、local package round-trip，以及 commit-bound Windows／Linux CI 與 checksum comparison 完成驗證。此 disposition 不接受新的 residual risk，也不改變 SEC-F-006／007 或 Addendum 002 的 Mode B fail-closed boundary。

## Rollback and Remaining Work

- Rollback／forward-fix 依 Addendum 003；不得把 `tmp/` 加回公開 allowlist。
- 本 Evidence 更新形成的 follow-up commit 仍須通過 PR checks 後才能合併；不得跳過 PR workflow。
- TEST-WORKFLOW-002 cancellation run 與其 cleanup／privacy Evidence 仍待執行。
- 正式 Approval merge、state transition、G5 submission 與 Release readiness仍未授權。
