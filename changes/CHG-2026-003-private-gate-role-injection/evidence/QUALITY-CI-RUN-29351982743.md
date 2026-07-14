# CHG-2026-003 Quality CI Run 29351982743

- Change：CHG-2026-003
- Commit：`ac543f764345e837beeef0c1c7ddfeb1c15b5dbb`
- Workflow：[SDD Quality Gates run 29351982743](https://github.com/opendata-taipei/sdd_spec/actions/runs/29351982743)
- Started：2026-07-14T17:00:39Z
- Completed：2026-07-14T17:02:04Z
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
- Clean-commit reconstructed SHA-256：`7c05b101a085ab7c29a0c7f01e30ffcff04e1ab6584e80c631c6434feac92506`
- Entry count：252
- Windows artifact wrapper digest：`sha256:a464f50f6d749cd63d37db4af7f660c5dcc9f21ecbf32aa99189573511e4d737`
- Linux artifact wrapper digest：`sha256:3f5129a69e72a2e0414e283a5701baf76b888c05ac2f05f50499eba7a75bd0f8`
- Runtime audit artifact wrapper digest：`sha256:87fab5c1be9cae2319e67e83974fd5db7eef665b1be023fce324fb522e1a21c3`

公開 GitHub API 證明 workflow 與四個 jobs 均成功；`compare-package-checksums` success 證明 Windows／Linux package sidecar hashes 相同。Artifact wrapper digest 是 GitHub artifact archive 的 digest，不等同內部 Starter Kit ZIP hash。

Clean-commit archive hash 由相同 commit 的乾淨工作樹重新執行 `scripts/package_starter_kit.py build` 取得；safe verify／governance round trip 已在本地與兩個 CI matrix jobs 通過。

## Security Boundary

Quality workflow 不注入真實 role map、pepper 或 GitHub OIDC Approval context。本證據證明跨平台 implementation／packaging baseline，不取代 protected `SDD Gate Approval` 的 TEST-WORKFLOW-001、cancellation log、privacy artifact inspection 或 TASK-005 remediation pilot。
