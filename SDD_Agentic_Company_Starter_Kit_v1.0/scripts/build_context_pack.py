#!/usr/bin/env python3
from __future__ import annotations
import argparse
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

parser = argparse.ArgumentParser()
parser.add_argument('--change', required=True)
parser.add_argument('--output')
args = parser.parse_args()
choices = [d for d in (ROOT/'changes').glob(args.change+'*') if d.is_dir()]
if len(choices) != 1:
    raise SystemExit(f'Expected exactly one change directory, found {len(choices)}')
change = choices[0]
files = [
    ROOT/'constitution/project-constitution.md',
    ROOT/'constitution/ai-execution-contract.md',
    ROOT/'constitution/tool-portability-standard.md',
    ROOT/'specs/living/_index.yaml',
    change/'manifest.yaml', change/'proposal.md', change/'requirements.md', change/'nfr.md',
    change/'design.md', change/'tasks.md', change/'test-plan.md', change/'release-plan.md', change/'state.json'
]
parts = [f'# Context Pack — {change.name}\n\nGenerated: {datetime.now().isoformat()}\n']
for p in files:
    if p.exists():
        rel = p.relative_to(ROOT)
        parts.append(f'\n---\n\n## FILE: `{rel}`\n\n```{p.suffix.lstrip(".")}\n{p.read_text(encoding="utf-8")}\n```\n')
out = Path(args.output) if args.output else ROOT/'reports/context'/f'{change.name}-context-pack.md'
if not out.is_absolute(): out = ROOT/out
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(''.join(parts), encoding='utf-8')
print(out.relative_to(ROOT))
