"""Automated checks for the Day 2 bulk file renamer."""

from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from main import (
    RenameError,
    build_rename_plan,
    default_manifest_path,
    execute_plan,
    load_undo_plan,
    parse_arguments,
    run_rename,
    run_undo,
    write_manifest,
)


class Arguments:
    """Minimal namespace substitute for direct command-handler checks."""

    def __init__(self, **values: object) -> None:
        self.__dict__.update(values)


class BulkFileRenamerTests(unittest.TestCase):
    """Verify planning, safety guarantees, application, and undo."""

    def test_preview_is_immutable_and_preserves_extensions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "report-draft.txt").write_text("text", encoding="utf-8")
            (root / "report-draft.csv").write_text("csv", encoding="utf-8")
            (root / "photo-draft.png").write_bytes(b"image")
            (root / "nested").mkdir()
            (root / "nested" / "report-draft.txt").write_text("protected", encoding="utf-8")

            output = io.StringIO()
            status = run_rename(
                Arguments(directory=root, find="-draft", replace="-final", pattern="*.txt", apply=False, manifest=None),
                output,
            )

            self.assertEqual(0, status)
            self.assertTrue((root / "report-draft.txt").is_file())
            self.assertFalse((root / "report-final.txt").exists())
            self.assertTrue((root / "report-draft.csv").is_file())
            self.assertTrue((root / "nested" / "report-draft.txt").is_file())
            self.assertIn("report-draft.txt -> report-final.txt", output.getvalue())
            self.assertIn("No se realizaron cambios", output.getvalue())

    def test_parser_accepts_dash_prefixed_find_and_replace_values(self) -> None:
        arguments = parse_arguments(
            [
                "rename",
                "projects/day-02-bulk-file-renamer/data/fixture-files",
                "--find",
                "-draft",
                "--replace",
                "-final",
                "--pattern",
                "*.txt",
            ]
        )

        self.assertEqual("-draft", arguments.find)
        self.assertEqual("-final", arguments.replace)
        self.assertEqual("*.txt", arguments.pattern)
        self.assertFalse(arguments.apply)

    def test_parser_accepts_multiple_dashes_equals_syntax_and_empty_replace(self) -> None:
        arguments = parse_arguments(
            ["rename", "directory", "--find", "---draft", "--replace=", "--apply"]
        )

        self.assertEqual("---draft", arguments.find)
        self.assertEqual("", arguments.replace)
        self.assertTrue(arguments.apply)

    def test_apply_writes_manifest_and_undo_restores_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "invoice-old.pdf").write_bytes(b"pdf")
            (root / "notes-old.txt").write_text("notes", encoding="utf-8")
            manifest = default_manifest_path(root)

            apply_output = io.StringIO()
            status = run_rename(
                Arguments(directory=root, find="-old", replace="-new", pattern="*", apply=True, manifest=None),
                apply_output,
            )

            self.assertEqual(0, status)
            self.assertTrue((root / "invoice-new.pdf").is_file())
            self.assertTrue((root / "notes-new.txt").is_file())
            self.assertTrue(manifest.is_file())
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual("rename", payload["operation"])
            self.assertEqual(2, len(payload["entries"]))

            preview_output = io.StringIO()
            self.assertEqual(0, run_undo(Arguments(manifest=manifest, apply=False), preview_output))
            self.assertTrue((root / "invoice-new.pdf").is_file())
            self.assertIn("No se realizaron cambios", preview_output.getvalue())

            undo_output = io.StringIO()
            self.assertEqual(0, run_undo(Arguments(manifest=manifest, apply=True), undo_output))
            self.assertTrue((root / "invoice-old.pdf").is_file())
            self.assertTrue((root / "notes-old.txt").is_file())
            self.assertFalse((root / "invoice-new.pdf").exists())

    def test_rejects_existing_target_and_duplicate_targets(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "alpha-old.txt").write_text("candidate", encoding="utf-8")
            (root / "alpha-new.txt").write_text("protected", encoding="utf-8")
            with self.assertRaisesRegex(RenameError, "no se sobrescribirá"):
                build_rename_plan(root, "-old", "-new")

        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            first = root / "first.txt"
            second = root / "second.txt"
            first.write_text("one", encoding="utf-8")
            second.write_text("two", encoding="utf-8")
            from main import RenameEntry, RenamePlan, validate_plan

            duplicate_plan = RenamePlan(
                root,
                (RenameEntry(first, root / "shared.txt"), RenameEntry(second, root / "shared.txt")),
            )
            with self.assertRaisesRegex(RenameError, "mismo destino"):
                validate_plan(duplicate_plan)

    def test_supports_a_swap_through_temporary_staging(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            left = root / "left.txt"
            right = root / "right.txt"
            left.write_text("left", encoding="utf-8")
            right.write_text("right", encoding="utf-8")

            from main import RenameEntry, RenamePlan

            plan = RenamePlan(root, (RenameEntry(left, right), RenameEntry(right, left)))
            execute_plan(plan)
            self.assertEqual("right", left.read_text(encoding="utf-8"))
            self.assertEqual("left", right.read_text(encoding="utf-8"))

    def test_invalid_directory_empty_find_and_stale_manifest_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            with self.assertRaises(RenameError):
                build_rename_plan(root / "missing", "a", "b")
            with self.assertRaisesRegex(RenameError, "no puede estar vacío"):
                build_rename_plan(root, "", "b")

            source = root / "before.txt"
            source.write_text("fixture", encoding="utf-8")
            plan = build_rename_plan(root, "before", "after")
            execute_plan(plan)
            manifest = root / "record.json"
            write_manifest(plan, manifest, "rename")
            (root / "after.txt").unlink()
            with self.assertRaisesRegex(RenameError, "falta el archivo"):
                load_undo_plan(manifest)


if __name__ == "__main__":
    unittest.main()
