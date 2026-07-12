#!/usr/bin/env python3
from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def git_changed() -> list[str]:
    commands = [
        ["git", "diff", "--name-only", "HEAD"],
        ["git", "diff", "--name-only", "--cached"],
    ]
    files = set()
    for cmd in commands:
        result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
        if result.returncode == 0:
            files.update(x.strip() for x in result.stdout.splitlines() if x.strip())
    return sorted(files)

def declared_files(change_dir: Path) -> set[str]:
    p = change_dir / "manifest.yaml"
    if not p.exists():
        return set()
    lines = p.read_text(encoding="utf-8").splitlines()
    result, active = set(), False
    for line in lines:
        if line.startswith("declared_files:"):
            active = True
            continue
        if active:
            if line.startswith("  - "):
                result.add(line[4:].strip().strip("'\""))
            elif line and not line.startswith(" "):
                break
    return result

parser = argparse.ArgumentParser()
parser.add_argument("--change", required=True)
args = parser.parse_args()
choices = [d for d in (ROOT / "changes").glob(args.change + "*") if d.is_dir()]
if len(choices) != 1:
    print(f"ERROR: expected exactly one change directory for {args.change}, found {len(choices)}")
    sys.exit(2)
change_dir = choices[0]
changed = git_changed()
if not changed:
    print("No Git changes detected, or repository has not been initialized.")
    sys.exit(0)
declared = declared_files(change_dir)
ignored_prefixes = (str(change_dir.relative_to(ROOT)), ".github/", "reports/")
unspeced = [f for f in changed if not f.startswith(ignored_prefixes) and f not in declared]
tracked = [f for f in changed if f in declared]
print("Tracked drift:")
for f in tracked: print("  ", f)
print("Unspeced drift:")
for f in unspeced: print("  ", f)
if unspeced:
    print("Result: BLOCK — update manifest/spec or obtain approved exception")
    sys.exit(1)
print("Result: PASS")
