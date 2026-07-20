# CHG-2026-003 TASK-010 Post-Merge CI Run 29762747845

- Change：CHG-2026-003
- Task：TASK-010 synthetic contract only
- Merge commit：`c48680a0451a3efad204838222f51b2ef456dbd8`
- Pull Request：[#3](https://github.com/opendata-taipei/sdd_spec/pull/3)
- Workflow：[SDD Quality Gates run 29762747845](https://github.com/opendata-taipei/sdd_spec/actions/runs/29762747845)
- Event：push to `main`
- Started：2026-07-20T17:12:02Z
- Completed：2026-07-20T17:13:18Z
- Conclusion：success

## Job Results

| Job | Result |
|---|---|
| validate-sdd | success |
| package-round-trip (ubuntu-latest) | success |
| package-round-trip (windows-latest) | success |
| compare-package-checksums | success |

## Artifact Metadata

| Artifact | GitHub artifact digest | Size |
|---|---|---:|
| starter-kit-Windows | `sha256:141ab4ff94ac0ca43a232958c2cebb3ac96ca08581d4b47a8782d082b4d6affb` | 210276 bytes |
| starter-kit-Linux | `sha256:24e543f617a70c00eec6715edeedac03b706b9de908926e384ddff269f3ecc0b` | 210276 bytes |
| agent-runtime-audit-29762747845 | `sha256:39c3aa360d07cb6ea513ba3c591b434a33ec993139e1641ffb56c0daa9b40f75` | 3005 bytes |

GitHub artifact digest是artifact wrapper的完整性資訊，不等同Starter Kit ZIP內部hash。`compare-package-checksums` success證明本run的Windows／Linux archive sidecar hashes一致。

## Boundary

本Evidence只證明合併後main的synthetic implementation與跨平台package baseline。它不關閉SEC-F-013、016～022，不證明dedicated host、真實device OAuth、credential custody、ruleset source pinning或TASK-011，亦不授權production Mode B或formal Approval merge。
