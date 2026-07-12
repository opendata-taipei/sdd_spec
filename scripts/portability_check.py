#!/usr/bin/env python3
from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTHORITATIVE_DIRS = [ROOT / "constitution", ROOT / "specs", ROOT / "changes"]
# 正式規格可談到 AI 工具，但不得以私有聊天、隱藏記憶或工具專用命令作為必要依賴。
PATTERNS = {
    "implicit_chat_context": re.compile(r"(依照|如同|根據).{0,8}(先前|上次|之前).{0,8}(聊天|對話|討論)"),
    "private_memory": re.compile(r"(private memory|私有記憶|隱藏記憶)", re.I),
    "tool_command_in_spec": re.compile(r"/(spectra|sdd|spec):[a-z-]+", re.I),
}
violations = []
for base in AUTHORITATIVE_DIRS:
    for p in base.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in {".md", ".yaml", ".yml", ".json"}:
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        for name, pattern in PATTERNS.items():
            for m in pattern.finditer(text):
                line = text[:m.start()].count("\n") + 1
                violations.append((p.relative_to(ROOT), line, name, m.group(0)))
for item in violations:
    print(f"VIOLATION: {item[0]}:{item[1]} [{item[2]}] {item[3]}")
print(f"Portability check complete: {len(violations)} violation(s)")
sys.exit(1 if violations else 0)
