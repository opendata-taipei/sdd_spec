from __future__ import annotations

import importlib.util
import json
import stat
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "package_starter_kit", ROOT / "scripts" / "package_starter_kit.py"
)
assert SPEC and SPEC.loader
packaging = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(packaging)


class StarterKitPackagingTests(unittest.TestCase):
    def _fixture(self, parent: Path, name: str, line_endings: bytes = b"\n") -> Path:
        root = parent / name
        root.mkdir()
        files = ["KIT_MANIFEST.json", "note.txt", "payload.bin"]
        manifest = {
            "name": "SDD Agentic Company Starter Kit",
            "version": "9.9.9-test",
            "file_count": len(files),
            "files": files,
        }
        (root / "KIT_MANIFEST.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        logical = b"first\nsecond\n"
        if line_endings == b"\r\n":
            logical = b"\xef\xbb\xbffirst\r\nsecond\r\n"
        (root / "note.txt").write_bytes(logical)
        (root / "payload.bin").write_bytes(b"\x00\x01\xff\r\n")
        return root

    def test_build_is_deterministic_for_logical_text(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            first = self._fixture(parent, "first", b"\n")
            second = self._fixture(parent, "second", b"\r\n")
            first_outputs = packaging.build_package(first, parent / "out-first")
            second_outputs = packaging.build_package(second, parent / "out-second")
            self.assertEqual(
                first_outputs["archive"].read_bytes(), second_outputs["archive"].read_bytes()
            )
            self.assertEqual(
                first_outputs["metadata"].read_bytes(), second_outputs["metadata"].read_bytes()
            )
            self.assertEqual(
                first_outputs["checksum"].read_bytes(), second_outputs["checksum"].read_bytes()
            )

    def test_build_uses_approved_zip_profile_and_external_sidecars(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            root = self._fixture(parent, "source")
            outputs = packaging.build_package(root, parent / "out")
            with zipfile.ZipFile(outputs["archive"]) as archive:
                self.assertEqual(archive.comment, b"")
                self.assertEqual(archive.namelist(), ["KIT_MANIFEST.json", "note.txt", "payload.bin"])
                for info in archive.infolist():
                    self.assertEqual(info.compress_type, zipfile.ZIP_STORED)
                    self.assertEqual(info.date_time, packaging.FIXED_TIMESTAMP)
                    self.assertEqual((info.external_attr >> 16) & 0xFFFF, stat.S_IFREG | 0o644)
                self.assertNotIn(outputs["metadata"].name, archive.namelist())
                self.assertNotIn(outputs["checksum"].name, archive.namelist())

    def test_verify_extracts_only_after_complete_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            root = self._fixture(parent, "source")
            outputs = packaging.build_package(root, parent / "out")
            destination = parent / "verified"
            report = packaging.verify_package(outputs["archive"], destination=destination)
            self.assertEqual(report["entry_count"], 3)
            self.assertEqual((destination / "note.txt").read_bytes(), b"first\nsecond\n")
            self.assertFalse((destination / ".git").exists())

    def test_archive_tampering_is_rejected_without_destination(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            outputs = packaging.build_package(self._fixture(parent, "source"), parent / "out")
            data = bytearray(outputs["archive"].read_bytes())
            data[len(data) // 2] ^= 1
            outputs["archive"].write_bytes(data)
            destination = parent / "must-not-exist"
            with self.assertRaises(packaging.PackageValidationError):
                packaging.verify_package(outputs["archive"], destination=destination)
            self.assertFalse(destination.exists())

    def test_metadata_entry_hash_tampering_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            outputs = packaging.build_package(self._fixture(parent, "source"), parent / "out")
            metadata = json.loads(outputs["metadata"].read_text(encoding="utf-8"))
            metadata["entries"][0]["sha256"] = "0" * 64
            outputs["metadata"].write_bytes(packaging._canonical_json_bytes(metadata))
            with self.assertRaises(packaging.PackageValidationError):
                packaging.verify_package(outputs["archive"])

    def test_unsafe_and_portability_colliding_paths_are_rejected(self) -> None:
        unsafe = [
            "../escape.txt", "/absolute.txt", "C:/drive.txt", "dir\\file.txt",
            "dot/./file", "NUL.txt", "trailing./file", "bad\x00name", "dir/file:ads",
        ]
        for path in unsafe:
            with self.subTest(path=path), self.assertRaises(packaging.PackageValidationError):
                packaging._validate_path(path)
        with self.assertRaises(packaging.PackageValidationError):
            packaging._validate_unique_paths(["Docs/README.md", "docs/readme.md"])

    def test_symlink_and_directory_profiles_are_rejected(self) -> None:
        symlink = packaging._zip_info("link")
        symlink.external_attr = (stat.S_IFLNK | 0o777) << 16
        directory = packaging._zip_info("directory")
        directory.external_attr = (stat.S_IFDIR | 0o755) << 16
        for info in (symlink, directory):
            with self.assertRaises(packaging.PackageValidationError):
                packaging._validate_zip_profile(info)

    def test_governance_failure_cleans_staging_and_destination(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            outputs = packaging.build_package(self._fixture(parent, "source"), parent / "out")
            destination = parent / "verified"
            with mock.patch.object(
                packaging,
                "_run_governance_checks",
                side_effect=packaging.PackageValidationError("expected failure"),
            ):
                with self.assertRaises(packaging.PackageValidationError):
                    packaging.verify_package(
                        outputs["archive"], destination=destination, run_governance=True
                    )
            self.assertFalse(destination.exists())
            self.assertEqual(list(parent.glob(".verified.staging-*")), [])

    def test_existing_outputs_and_destination_are_never_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            root = self._fixture(parent, "source")
            outputs = packaging.build_package(root, parent / "out")
            with self.assertRaises(FileExistsError):
                packaging.build_package(root, parent / "out")
            destination = parent / "existing"
            destination.mkdir()
            marker = destination / "marker"
            marker.write_text("keep", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                packaging.verify_package(outputs["archive"], destination=destination)
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep")

    def test_metadata_limits_are_independent_of_declared_values(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            outputs = packaging.build_package(self._fixture(parent, "source"), parent / "out")
            metadata = json.loads(outputs["metadata"].read_text(encoding="utf-8"))
            metadata["entries"][0]["size"] = packaging.MAX_ENTRY_SIZE + 1
            metadata["archive"]["total_uncompressed_size"] = sum(
                entry["size"] for entry in metadata["entries"]
            )
            with self.assertRaises(packaging.PackageValidationError):
                packaging._validate_metadata(
                    packaging._canonical_json_bytes(metadata), outputs["archive"].name
                )


if __name__ == "__main__":
    unittest.main()
