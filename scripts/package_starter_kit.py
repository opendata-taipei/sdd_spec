#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unicodedata
import zipfile
from pathlib import Path
from typing import BinaryIO

ROOT = Path(__file__).resolve().parents[1]
FORMAT_VERSION = "1.0"
MAX_ENTRIES = 4096
MAX_ENTRY_SIZE = 32 * 1024 * 1024
MAX_TOTAL_SIZE = 256 * 1024 * 1024
BUFFER_SIZE = 1024 * 1024
FIXED_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
REGULAR_MODE = stat.S_IFREG | 0o644
TEXT_SUFFIXES = {
    ".md", ".txt", ".json", ".jsonl", ".yaml", ".yml", ".py",
    ".toml", ".ini", ".cfg",
}
TEXT_BASENAMES = {".editorconfig", ".gitignore"}
WINDOWS_DEVICES = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}
VERSION_RE = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?")
SHA256_RE = re.compile(r"[a-f0-9]{64}")


class PackageValidationError(ValueError):
    """The package or source manifest violates the approved contract."""


def _sort_key(value: str) -> tuple[str, str]:
    return value.casefold(), value


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(BUFFER_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def _validate_path(path: str) -> None:
    if not isinstance(path, str) or not path:
        raise PackageValidationError("entry path must be a non-empty string")
    if path != unicodedata.normalize("NFC", path):
        raise PackageValidationError(f"entry path is not Unicode NFC: {path!r}")
    if "\x00" in path or "\\" in path or ":" in path:
        raise PackageValidationError(f"entry path contains NUL, backslash, or colon: {path!r}")
    if path.startswith("/") or re.match(r"^[A-Za-z]:", path):
        raise PackageValidationError(f"entry path is absolute or drive-prefixed: {path!r}")
    if path.endswith("/"):
        raise PackageValidationError(f"directory entries are forbidden: {path!r}")
    segments = path.split("/")
    if any(segment in {"", ".", ".."} for segment in segments):
        raise PackageValidationError(f"entry path contains an unsafe segment: {path!r}")
    for segment in segments:
        if segment.endswith((".", " ")):
            raise PackageValidationError(f"entry segment ends in dot or space: {path!r}")
        if segment.split(".", 1)[0].upper() in WINDOWS_DEVICES:
            raise PackageValidationError(f"entry uses a Windows device name: {path!r}")


def _validate_unique_paths(paths: list[str]) -> None:
    exact: set[str] = set()
    portable: set[str] = set()
    for path in paths:
        _validate_path(path)
        folded = unicodedata.normalize("NFC", path).casefold()
        if path in exact:
            raise PackageValidationError(f"duplicate entry path: {path}")
        if folded in portable:
            raise PackageValidationError(f"portable path collision: {path}")
        exact.add(path)
        portable.add(folded)


def _load_manifest(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PackageValidationError(f"invalid Kit Manifest: {exc}") from exc
    if not isinstance(value, dict):
        raise PackageValidationError("Kit Manifest must be an object")
    required = {"name", "version", "file_count", "files"}
    if set(value) != required:
        raise PackageValidationError("Kit Manifest has missing or additional properties")
    version = value.get("version")
    files = value.get("files")
    count = value.get("file_count")
    if not isinstance(version, str) or VERSION_RE.fullmatch(version) is None:
        raise PackageValidationError("Kit Manifest version is not filename-safe")
    if not isinstance(files, list) or not all(isinstance(item, str) for item in files):
        raise PackageValidationError("Kit Manifest files must be a string array")
    if type(count) is not int or count != len(files):
        raise PackageValidationError("Kit Manifest file_count does not match files")
    if count > MAX_ENTRIES:
        raise PackageValidationError("Kit Manifest exceeds the entry limit")
    _validate_unique_paths(files)
    if files != sorted(files, key=_sort_key):
        raise PackageValidationError("Kit Manifest files are not canonically sorted")
    if "KIT_MANIFEST.json" not in files:
        raise PackageValidationError("Kit Manifest must include itself")
    return value


def _is_link_like(path: Path) -> bool:
    if path.is_symlink():
        return True
    is_junction = getattr(path, "is_junction", None)
    return bool(is_junction and is_junction())


def _source_file(root: Path, relative: str) -> Path:
    current = root
    for segment in relative.split("/"):
        current = current / segment
        if _is_link_like(current):
            raise PackageValidationError(f"symlink or junction source is forbidden: {relative}")
    try:
        resolved = current.resolve(strict=True)
        resolved.relative_to(root)
    except (OSError, ValueError) as exc:
        raise PackageValidationError(f"source escapes root or is missing: {relative}") from exc
    try:
        mode = resolved.stat().st_mode
    except OSError as exc:
        raise PackageValidationError(f"cannot stat source: {relative}") from exc
    if not stat.S_ISREG(mode):
        raise PackageValidationError(f"source is not a regular file: {relative}")
    return resolved


def _canonical_source_bytes(path: Path, relative: str) -> bytes:
    data = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES or path.name in TEXT_BASENAMES:
        try:
            text = data.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise PackageValidationError(f"approved text file is not UTF-8: {relative}") from exc
        data = text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
    if len(data) > MAX_ENTRY_SIZE:
        raise PackageValidationError(f"source exceeds per-entry limit: {relative}")
    return data


def _zip_info(path: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(path, date_time=FIXED_TIMESTAMP)
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.create_version = 20
    info.extract_version = 20
    info.external_attr = REGULAR_MODE << 16
    info.internal_attr = 0
    info.extra = b""
    info.comment = b""
    return info


def build_package(
    root: Path = ROOT,
    output_dir: Path | None = None,
    force: bool = False,
) -> dict[str, Path]:
    root = root.resolve(strict=True)
    manifest_path = (root / "KIT_MANIFEST.json").resolve(strict=True)
    manifest = _load_manifest(manifest_path)
    output_dir = (output_dir or root / "dist").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    base = f"sdd-agentic-starter-kit-{manifest['version']}"
    archive_path = output_dir / f"{base}.zip"
    metadata_path = output_dir / f"{base}.metadata.json"
    checksum_path = output_dir / f"{base}.zip.sha256"
    targets = [archive_path, metadata_path, checksum_path]
    if not force and any(path.exists() for path in targets):
        raise FileExistsError("package output already exists; use --force to replace it")

    entries: list[dict] = []
    content: list[tuple[str, bytes]] = []
    total = 0
    for relative in manifest["files"]:
        data = _canonical_source_bytes(_source_file(root, relative), relative)
        total += len(data)
        if total > MAX_TOTAL_SIZE:
            raise PackageValidationError("package exceeds the total size limit")
        content.append((relative, data))
        entries.append({"path": relative, "size": len(data), "sha256": _sha256_bytes(data)})

    created: list[Path] = []
    mode = "wb" if force else "xb"
    try:
        with archive_path.open(mode) as archive_stream:
            created.append(archive_path)
            with zipfile.ZipFile(archive_stream, "w", compression=zipfile.ZIP_STORED, allowZip64=False) as package:
                package.comment = b""
                for relative, data in content:
                    package.writestr(_zip_info(relative), data)
        archive_hash = _sha256_file(archive_path)
        manifest_entry = next(item for item in entries if item["path"] == "KIT_MANIFEST.json")
        metadata = {
            "format_version": FORMAT_VERSION,
            "kit_version": manifest["version"],
            "source_manifest_sha256": manifest_entry["sha256"],
            "archive": {
                "basename": archive_path.name,
                "sha256": archive_hash,
                "entry_count": len(entries),
                "total_uncompressed_size": total,
            },
            "entries": entries,
        }
        with metadata_path.open(mode) as stream:
            created.append(metadata_path)
            stream.write(_canonical_json_bytes(metadata))
        with checksum_path.open(mode) as stream:
            created.append(checksum_path)
            stream.write(f"{archive_hash}  {archive_path.name}\n".encode("ascii"))
    except Exception:
        for path in created:
            try:
                path.unlink()
            except OSError:
                pass
        raise
    return {"archive": archive_path, "metadata": metadata_path, "checksum": checksum_path}


def _require_exact_keys(value: object, keys: set[str], label: str) -> dict:
    if not isinstance(value, dict) or set(value) != keys:
        raise PackageValidationError(f"{label} has missing or additional properties")
    return value


def _validate_metadata(raw: bytes, archive_name: str) -> dict:
    try:
        metadata = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise PackageValidationError(f"invalid metadata JSON: {exc}") from exc
    if raw != _canonical_json_bytes(metadata):
        raise PackageValidationError("metadata JSON is not canonical")
    metadata = _require_exact_keys(
        metadata,
        {"format_version", "kit_version", "source_manifest_sha256", "archive", "entries"},
        "metadata",
    )
    if metadata["format_version"] != FORMAT_VERSION:
        raise PackageValidationError("unsupported metadata format_version")
    if not isinstance(metadata["kit_version"], str) or VERSION_RE.fullmatch(metadata["kit_version"]) is None:
        raise PackageValidationError("metadata kit_version is invalid")
    if not isinstance(metadata["source_manifest_sha256"], str) or SHA256_RE.fullmatch(metadata["source_manifest_sha256"]) is None:
        raise PackageValidationError("metadata source manifest hash is invalid")
    archive = _require_exact_keys(
        metadata["archive"],
        {"basename", "sha256", "entry_count", "total_uncompressed_size"},
        "metadata archive",
    )
    if archive["basename"] != archive_name:
        raise PackageValidationError("metadata archive basename does not match")
    if archive_name != f"sdd-agentic-starter-kit-{metadata['kit_version']}.zip":
        raise PackageValidationError("archive basename does not match kit_version")
    if not isinstance(archive["sha256"], str) or SHA256_RE.fullmatch(archive["sha256"]) is None:
        raise PackageValidationError("metadata archive hash is invalid")
    for key, maximum in (("entry_count", MAX_ENTRIES), ("total_uncompressed_size", MAX_TOTAL_SIZE)):
        if type(archive[key]) is not int or not 0 <= archive[key] <= maximum:
            raise PackageValidationError(f"metadata archive {key} is invalid")
    entries = metadata["entries"]
    if not isinstance(entries, list) or len(entries) > MAX_ENTRIES:
        raise PackageValidationError("metadata entries is invalid or exceeds the limit")
    paths: list[str] = []
    for entry in entries:
        entry = _require_exact_keys(entry, {"path", "size", "sha256"}, "metadata entry")
        if not isinstance(entry["path"], str):
            raise PackageValidationError("metadata entry path must be a string")
        if type(entry["size"]) is not int or not 0 <= entry["size"] <= MAX_ENTRY_SIZE:
            raise PackageValidationError(f"metadata entry size is invalid: {entry['path']}")
        if not isinstance(entry["sha256"], str) or SHA256_RE.fullmatch(entry["sha256"]) is None:
            raise PackageValidationError(f"metadata entry hash is invalid: {entry['path']}")
        paths.append(entry["path"])
    _validate_unique_paths(paths)
    if paths != sorted(paths, key=_sort_key):
        raise PackageValidationError("metadata entries are not canonically sorted")
    if archive["entry_count"] != len(entries):
        raise PackageValidationError("metadata entry_count does not match entries")
    if archive["total_uncompressed_size"] != sum(item["size"] for item in entries):
        raise PackageValidationError("metadata total size does not match entries")
    return metadata


def _validate_checksum(raw: bytes, archive_name: str) -> str:
    try:
        value = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise PackageValidationError("checksum sidecar is not ASCII") from exc
    match = re.fullmatch(r"([a-f0-9]{64})  ([^\r\n]+)\n", value)
    if match is None or match.group(2) != archive_name:
        raise PackageValidationError("checksum sidecar format or basename is invalid")
    return match.group(1)


def _validate_zip_profile(info: zipfile.ZipInfo) -> None:
    original = getattr(info, "orig_filename", info.filename)
    if "\x00" in original or original != info.filename:
        raise PackageValidationError("ZIP entry contains a NUL byte")
    _validate_path(info.filename)
    if info.flag_bits & 0x1:
        raise PackageValidationError(f"encrypted ZIP entry is forbidden: {info.filename}")
    if info.flag_bits & ~0x800:
        raise PackageValidationError(f"ZIP entry uses unsupported flags: {info.filename}")
    if info.is_dir() or stat.S_ISDIR((info.external_attr >> 16) & 0xFFFF):
        raise PackageValidationError(f"directory ZIP entry is forbidden: {info.filename}")
    mode = (info.external_attr >> 16) & 0xFFFF
    if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
        raise PackageValidationError(f"non-regular ZIP entry is forbidden: {info.filename}")
    if (
        info.compress_type != zipfile.ZIP_STORED
        or info.compress_size != info.file_size
        or info.date_time != FIXED_TIMESTAMP
        or info.create_system != 3
        or mode != REGULAR_MODE
        or info.extra
        or info.comment
    ):
        raise PackageValidationError(f"ZIP entry violates deterministic profile: {info.filename}")
    if info.file_size > MAX_ENTRY_SIZE:
        raise PackageValidationError(f"ZIP entry exceeds the size limit: {info.filename}")


def _stream_entry(package: zipfile.ZipFile, info: zipfile.ZipInfo) -> tuple[str, bytes | None]:
    digest = hashlib.sha256()
    size = 0
    manifest_data: bytearray | None = bytearray() if info.filename == "KIT_MANIFEST.json" else None
    with package.open(info, "r") as stream:
        for chunk in iter(lambda: stream.read(BUFFER_SIZE), b""):
            size += len(chunk)
            if size > info.file_size or size > MAX_ENTRY_SIZE:
                raise PackageValidationError(f"ZIP entry expands beyond its limit: {info.filename}")
            digest.update(chunk)
            if manifest_data is not None:
                manifest_data.extend(chunk)
    if size != info.file_size:
        raise PackageValidationError(f"ZIP entry actual size mismatch: {info.filename}")
    return digest.hexdigest(), bytes(manifest_data) if manifest_data is not None else None


def _run_governance_checks(root: Path) -> None:
    commands = [
        [sys.executable, "scripts/build_kit_manifest.py", "--check"],
        [sys.executable, "scripts/validate_sdd.py"],
        [sys.executable, "scripts/validate_enterprise.py"],
        [sys.executable, "scripts/portability_check.py"],
    ]
    for command in commands:
        result = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        if result.returncode != 0:
            raise PackageValidationError(f"governance command failed: {' '.join(command[1:])}")


def _extract_verified(package: zipfile.ZipFile, infos: list[zipfile.ZipInfo], destination: Path, run_governance: bool) -> None:
    destination = destination.resolve()
    if destination.exists():
        raise FileExistsError(f"destination already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{destination.name}.staging-", dir=destination.parent))
    try:
        for info in infos:
            target = staging.joinpath(*info.filename.split("/"))
            target.parent.mkdir(parents=True, exist_ok=True)
            with package.open(info, "r") as source, target.open("xb") as output:
                shutil.copyfileobj(source, output, length=BUFFER_SIZE)
        if run_governance:
            _run_governance_checks(staging)
        if destination.exists():
            raise FileExistsError(f"destination appeared during extraction: {destination}")
        staging.rename(destination)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def verify_package(
    archive_path: Path,
    metadata_path: Path | None = None,
    checksum_path: Path | None = None,
    destination: Path | None = None,
    run_governance: bool = False,
) -> dict:
    archive_path = archive_path.resolve(strict=True)
    if archive_path.suffix.lower() != ".zip":
        raise PackageValidationError("archive filename must end in .zip")
    prefix = archive_path.name[:-4]
    metadata_path = (metadata_path or archive_path.with_name(f"{prefix}.metadata.json")).resolve(strict=True)
    checksum_path = (checksum_path or archive_path.with_name(f"{prefix}.zip.sha256")).resolve(strict=True)
    if run_governance and destination is None:
        raise PackageValidationError("--run-governance requires --destination")
    metadata = _validate_metadata(metadata_path.read_bytes(), archive_path.name)
    checksum_hash = _validate_checksum(checksum_path.read_bytes(), archive_path.name)
    archive_hash = _sha256_file(archive_path)
    if archive_hash != checksum_hash or archive_hash != metadata["archive"]["sha256"]:
        raise PackageValidationError("archive SHA-256 does not match both sidecars")

    try:
        with zipfile.ZipFile(archive_path, "r") as package:
            if package.comment:
                raise PackageValidationError("ZIP archive comment must be empty")
            infos = package.infolist()
            if len(infos) > MAX_ENTRIES:
                raise PackageValidationError("ZIP exceeds the entry count limit")
            paths = [info.filename for info in infos]
            _validate_unique_paths(paths)
            if paths != sorted(paths, key=_sort_key):
                raise PackageValidationError("ZIP entries are not canonically sorted")
            for info in infos:
                _validate_zip_profile(info)
            if sum(info.file_size for info in infos) > MAX_TOTAL_SIZE:
                raise PackageValidationError("ZIP exceeds the total size limit")

            metadata_entries = metadata["entries"]
            expected = {item["path"]: item for item in metadata_entries}
            if paths != [item["path"] for item in metadata_entries]:
                raise PackageValidationError("ZIP and metadata entry sets differ")
            if len(infos) != metadata["archive"]["entry_count"]:
                raise PackageValidationError("ZIP entry count differs from metadata")
            manifest_bytes: bytes | None = None
            for info in infos:
                declared = expected[info.filename]
                if info.file_size != declared["size"]:
                    raise PackageValidationError(f"ZIP entry size differs from metadata: {info.filename}")
                digest, captured = _stream_entry(package, info)
                if digest != declared["sha256"]:
                    raise PackageValidationError(f"ZIP entry hash differs from metadata: {info.filename}")
                if captured is not None:
                    manifest_bytes = captured
            if manifest_bytes is None or _sha256_bytes(manifest_bytes) != metadata["source_manifest_sha256"]:
                raise PackageValidationError("source Kit Manifest hash does not match")
            with tempfile.TemporaryDirectory() as temporary:
                manifest_file = Path(temporary) / "KIT_MANIFEST.json"
                manifest_file.write_bytes(manifest_bytes)
                manifest = _load_manifest(manifest_file)
            if manifest["version"] != metadata["kit_version"]:
                raise PackageValidationError("Kit Manifest and metadata versions differ")
            if manifest["files"] != paths:
                raise PackageValidationError("Kit Manifest and ZIP entry sets differ")
            if destination is not None:
                _extract_verified(package, infos, destination, run_governance)
    except (zipfile.BadZipFile, zipfile.LargeZipFile, RuntimeError) as exc:
        raise PackageValidationError(f"invalid ZIP archive: {exc}") from exc
    return {
        "archive": str(archive_path),
        "sha256": archive_hash,
        "entry_count": len(metadata["entries"]),
        "total_uncompressed_size": metadata["archive"]["total_uncompressed_size"],
        "destination": str(destination.resolve()) if destination is not None else None,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build or safely verify the SDD Starter Kit package")
    subparsers = parser.add_subparsers(dest="command", required=True)
    build_parser = subparsers.add_parser("build", help="build deterministic ZIP and sidecars")
    build_parser.add_argument("--root", type=Path, default=ROOT)
    build_parser.add_argument("--output-dir", type=Path)
    build_parser.add_argument("--force", action="store_true")
    verify_parser = subparsers.add_parser("verify", help="verify before optionally extracting")
    verify_parser.add_argument("archive", type=Path)
    verify_parser.add_argument("--metadata", type=Path)
    verify_parser.add_argument("--checksum", type=Path)
    verify_parser.add_argument("--destination", type=Path)
    verify_parser.add_argument("--run-governance", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "build":
            outputs = build_package(args.root, args.output_dir, args.force)
            for label, path in outputs.items():
                print(f"{label}: {path}")
        else:
            report = verify_package(
                args.archive, args.metadata, args.checksum, args.destination, args.run_governance
            )
            print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    except PackageValidationError as exc:
        print(f"PACKAGE VALIDATION FAILED: {exc}", file=sys.stderr)
        return 3
    except (FileExistsError, FileNotFoundError, OSError) as exc:
        print(f"PACKAGE I/O FAILED: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
