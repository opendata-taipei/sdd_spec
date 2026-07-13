# Package CI Run 29268981993

- Change：CHG-2026-002
- Commit：`74448ddc5eb6f8511251ce2213aeb5152f4c0c27`
- Workflow：[SDD Quality Gates run 29268981993](https://github.com/opendata-taipei/sdd_spec/actions/runs/29268981993)
- Started：2026-07-13T17:04:24Z
- Completed：2026-07-13T17:05:30Z
- Conclusion：success

## Job Results

| Job | Result |
|---|---|
| validate-sdd | success |
| package-round-trip (ubuntu-latest) | success |
| package-round-trip (windows-latest) | success |
| compare-package-checksums | success |

## Deterministic Archive

- Archive：`sdd-agentic-starter-kit-1.5.0-dev.zip`
- Clean-commit reconstructed SHA-256：`0d8f82429a2ac970adad5c6d2e42feaac7aafe00a119ea8b4127a38f9246d1fc`
- Entry count：216

公開 API 可驗證 workflow 與四個 job 均成功，但未登入時 GitHub 不允許下載 job log／artifact。上述 archive hash 是由相同 commit 的 Git blobs 透過 `git archive` 建立乾淨來源，再執行 `scripts/package_starter_kit.py build` 所重現；CI 的 comparison success 則獨立證明 Windows 與 Linux sidecar hashes 相同。

## Security Note

本次證據只使用 GitHub 公開 API，未讀取或保存使用者 GitHub login、cookie、token 或私有 identity mapping。
