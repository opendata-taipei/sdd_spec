# CHG-2026-001 Manifest CI Gate — Local Verification Report

- Executed at：2026-07-12T15:46:51+00:00
- Environment：Windows, CPython 3.13.14
- Baseline commit：`e35e7e44bb4746c915fbd2895a89d46ee72912b0`
- Result：PASS

## Results

| Check | Result |
|---|---|
| Unit tests | 14 passed |
| Manifest-specific tests | 5 passed in 0.866s |
| SDD validation | 0 errors, 0 warnings |
| Enterprise validation | 0 errors, 0 warnings |
| Portability check | 0 violations |
| Agent governance evals | 4/4 passed |
| Runtime Audit validation | 2 runs, 0 errors |
| Manifest validation | 188 files, valid |
| Python compileall | Passed |

## Acceptance Coverage

- Valid Manifest returns success without modifying `KIT_MANIFEST.json`.
- An unmanaged file makes `--check` fail with the rebuild instruction.
- Runtime, Eval and Test outputs are excluded while unknown files remain managed by default.
- Sorting uses a deterministic case-sensitive tie-breaker after `casefold()`.
- Public role mapping contains a placeholder and no Email or GitHub token pattern.
- Manifest check completes below the five-second threshold in the local verification environment.

GitHub Actions execution remains required as release evidence after the implementation commit is pushed.
