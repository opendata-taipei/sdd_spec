#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "KIT_MANIFEST.json"
IGNORED_PARTS = {".git", ".venv", "__pycache__"}
IGNORED_TOP_LEVEL = {
    ".agents",
    ".codex",
    ".skills",
    "SDD原始來源研究文件包_v1.0",
}
IGNORED_ROOT_FILES = {"LICENSE", "SDD_規格開發架構.png"}
IGNORED_RUNTIME_PREFIXES = {
    "reports/runs/",
    "reports/test-",
    "reports/promotion-test-",
}
IGNORED_RUNTIME_FILES = {"reports/evals/latest.json"}


def manifest_sort_key(value: str) -> tuple[str, str]:
    return value.casefold(), value


def kit_files() -> list[str]:
    files = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in IGNORED_PARTS for part in path.parts):
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative.split("/", 1)[0] in IGNORED_TOP_LEVEL or relative in IGNORED_ROOT_FILES:
            continue
        if relative in IGNORED_RUNTIME_FILES or any(
            relative.startswith(prefix) for prefix in IGNORED_RUNTIME_PREFIXES
        ):
            continue
        files.append(relative)
    return sorted(files, key=manifest_sort_key)


def expected_manifest(version: str) -> dict:
    files = kit_files()
    return {
        "name": "SDD Agentic Company Starter Kit",
        "version": version,
        "file_count": len(files),
        "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build or verify KIT_MANIFEST.json")
    parser.add_argument("--version", default="1.4.1")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = expected_manifest(args.version)
    if args.check:
        actual = json.loads(MANIFEST.read_text(encoding="utf-8"))
        if actual != expected:
            print("KIT_MANIFEST.json is stale; run scripts/build_kit_manifest.py")
            return 1
        print(f"KIT manifest valid: {expected['file_count']} file(s), version {args.version}")
        return 0
    MANIFEST.write_text(
        json.dumps(expected, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"Wrote KIT_MANIFEST.json: {expected['file_count']} file(s), version {args.version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
