"""Unit and local integration coverage for the Phase 3 backup core."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from local_backup import run_local_backup  # noqa: E402
from models import VerificationResult  # noqa: E402
from verification import build_manifest, verify_copy  # noqa: E402


class LocalBackupTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temporary_directory.name)
        self.destination = self.workspace / "backups"
        self.destination.mkdir()
        self.fixtures = PROJECT_ROOT / "data" / "fixtures"
        self.expected = json.loads(
            (PROJECT_ROOT / "data" / "expected" / "local-copy-manifests.json").read_text(
                encoding="utf-8"
            )
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _assert_matches_reference(self, root: Path, scenario: str) -> None:
        reference = self.expected["manifests"][scenario]
        manifest = build_manifest(root)
        self.assertEqual(reference["root_type"], manifest.root_type)
        self.assertEqual(tuple(reference["directories"]), manifest.directories)
        self.assertEqual(
            [(item["relative_path"], item["size_bytes"]) for item in reference["files"]],
            [(entry.relative_path, entry.size_bytes) for entry in manifest.files],
        )

    def _temporary_entries(self) -> list[Path]:
        return list(self.destination.glob(".backup-v1-*.tmp"))

    def test_regular_file_success_matches_reference_and_preserves_source(self) -> None:
        source = self.fixtures / "regular-file" / "sample-note.txt"
        source_bytes = source.read_bytes()

        result = run_local_backup(source, self.destination)

        self.assertTrue(result.success)
        self.assertEqual(self.destination / source.name, result.final_path)
        self.assertEqual(source_bytes, source.read_bytes())
        self.assertEqual(source_bytes, result.final_path.read_bytes())
        self._assert_matches_reference(result.final_path, "regular-file-success")
        self.assertTrue(verify_copy(source, result.final_path).valid)

    def test_directory_tree_success_matches_reference_and_preserves_empty_directory(self) -> None:
        source = self.fixtures / "directory-tree"
        original_files = {path.relative_to(source): path.read_bytes() for path in source.rglob("*.txt")}

        result = run_local_backup(source, self.destination)

        self.assertTrue(result.success)
        self.assertTrue((result.final_path / "empty-folder").is_dir())
        self._assert_matches_reference(result.final_path, "directory-tree-success")
        self.assertTrue(verify_copy(source, result.final_path).valid)
        self.assertEqual(original_files, {path.relative_to(source): path.read_bytes() for path in source.rglob("*.txt")})

    def test_empty_directory_success(self) -> None:
        source = self.workspace / "empty-directory"
        source.mkdir()

        result = run_local_backup(source, self.destination)

        self.assertTrue(result.success)
        self.assertEqual([], list(result.final_path.iterdir()))
        self._assert_matches_reference(result.final_path, "empty-directory-success")

    def test_invalid_source_and_destination_cases_do_not_create_entries(self) -> None:
        missing = self.workspace / "missing"
        missing_result = run_local_backup(missing, self.destination)
        self.assertFalse(missing_result.success)
        self.assertEqual("validation-error", missing_result.error_code)

        source = self.fixtures / "regular-file" / "sample-note.txt"
        missing_destination = self.workspace / "absent-destination"
        destination_result = run_local_backup(source, missing_destination)
        self.assertFalse(destination_result.success)
        self.assertFalse(missing_destination.exists())

        file_destination = self.workspace / "destination-file"
        file_destination.write_text("unchanged", encoding="utf-8")
        file_result = run_local_backup(source, file_destination)
        self.assertFalse(file_result.success)
        self.assertEqual("unchanged", file_destination.read_text(encoding="utf-8"))

    def test_conflict_makes_second_execution_safe_and_idempotent(self) -> None:
        source = self.fixtures / "regular-file" / "sample-note.txt"
        first = run_local_backup(source, self.destination)
        original_backup = first.final_path.read_bytes()

        second = run_local_backup(source, self.destination)

        self.assertTrue(first.success)
        self.assertFalse(second.success)
        self.assertEqual("validation-error", second.error_code)
        self.assertEqual(original_backup, first.final_path.read_bytes())
        self.assertEqual([], self._temporary_entries())

    def test_forbidden_path_relationships_fail_before_copy(self) -> None:
        source = self.workspace / "source"
        source.mkdir()
        (source / "record.txt").write_text("fixture", encoding="utf-8")
        nested_destination = source / "nested-destination"
        nested_destination.mkdir()
        inside_result = run_local_backup(source, nested_destination)
        self.assertFalse(inside_result.success)

        parent = self.workspace / "parent"
        nested_source = parent / "child"
        nested_source.mkdir(parents=True)
        (nested_source / "record.txt").write_text("fixture", encoding="utf-8")
        ancestor_result = run_local_backup(nested_source, parent)
        self.assertFalse(ancestor_result.success)
        self.assertEqual([nested_source.name], [entry.name for entry in parent.iterdir()])

    def test_source_and_nested_symlinks_are_rejected_when_supported(self) -> None:
        target = self.workspace / "target.txt"
        target.write_text("safe", encoding="utf-8")
        source_link = self.workspace / "source-link"
        try:
            source_link.symlink_to(target)
        except (NotImplementedError, OSError):
            self.skipTest("symbolic links are unavailable in this environment")
        source_result = run_local_backup(source_link, self.destination)
        self.assertFalse(source_result.success)

        source_directory = self.workspace / "source-directory"
        source_directory.mkdir()
        (source_directory / "nested-link").symlink_to(target)
        nested_result = run_local_backup(source_directory, self.destination)
        self.assertFalse(nested_result.success)
        self.assertFalse((self.destination / source_directory.name).exists())

    def test_copy_verification_and_publication_failures_clean_owned_temporary_entries(self) -> None:
        source = self.fixtures / "regular-file" / "sample-note.txt"

        def interrupted_copy(plan, temporary_path):
            temporary_path.write_bytes(b"partial")
            raise OSError("injected copy interruption")

        copy_result = run_local_backup(source, self.destination, copy_operation=interrupted_copy)
        self.assertFalse(copy_result.success)
        self.assertEqual("copy-error", copy_result.error_code)
        self.assertEqual([], self._temporary_entries())

        mismatch_result = run_local_backup(
            source,
            self.destination,
            verify_operation=lambda _source, _copy: VerificationResult(False, "injected mismatch"),
        )
        self.assertFalse(mismatch_result.success)
        self.assertEqual("verification-error", mismatch_result.error_code)
        self.assertEqual([], self._temporary_entries())

        def failed_publish(_temporary_path, _final_path):
            raise OSError("injected publish failure")

        publish_result = run_local_backup(source, self.destination, publish_operation=failed_publish)
        self.assertFalse(publish_result.success)
        self.assertEqual("publication-error", publish_result.error_code)
        self.assertFalse((self.destination / source.name).exists())
        self.assertEqual([], self._temporary_entries())

    def test_verification_detects_changed_copy(self) -> None:
        source = self.fixtures / "regular-file" / "sample-note.txt"
        copied = self.workspace / "changed-copy.txt"
        shutil.copyfile(source, copied)
        copied.write_text("changed", encoding="utf-8")

        verification = verify_copy(source, copied)

        self.assertFalse(verification.valid)
        self.assertIn("differ", verification.reason)

    def test_local_core_remains_independent_from_the_optional_azure_adapter(self) -> None:
        catalog = json.loads((self.fixtures / "scenario-catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(3, len(catalog["azure_reserved_scenarios"]))
        self.assertTrue((SRC_ROOT / "azure_blob.py").exists())
        self.assertTrue((PROJECT_ROOT / "requirements.txt").exists())
        result = run_local_backup(self.fixtures / "regular-file" / "sample-note.txt", self.destination)
        self.assertTrue(result.success)


if __name__ == "__main__":
    unittest.main()
