"""Integration tests for the contract-v1 command-line interface."""

from __future__ import annotations

import io
import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC))

from main import run


class CommandLineTests(unittest.TestCase):
    """Verify CLI orchestration, channels, statuses, and file safety."""

    fixtures = PROJECT_ROOT / "data" / "fixtures"
    expected = PROJECT_ROOT / "data" / "expected"

    def test_preview_matches_reference_and_never_changes_working_copy(self) -> None:
        with self._working_copy("complex-valid.md") as target:
            before = target.read_bytes()
            status, stdout, stderr = self._run([str(target)])

            self.assertEqual(0, status)
            self.assertEqual(self._read_expected("complex-valid-preview.md"), stdout)
            self.assertEqual("", stderr)
            self.assertEqual(before, target.read_bytes())

    def test_write_updates_only_working_copy_and_repeated_execution_is_successful(self) -> None:
        fixture = self.fixtures / "complex-valid.md"
        fixture_hash = fixture.read_bytes()
        with self._working_copy("complex-valid.md") as target:
            status, stdout, stderr = self._run([str(target), "--write"])
            self.assertEqual(0, status)
            self.assertEqual("Índice actualizado.\n", stdout)
            self.assertEqual("", stderr)
            self.assertEqual(self._read_expected("complex-valid-preview.md"), target.read_bytes().decode("utf-8"))

            repeated_status, repeated_stdout, repeated_stderr = self._run([str(target), "--write"])
            self.assertEqual((0, "Índice actualizado.\n", ""), (repeated_status, repeated_stdout, repeated_stderr))
        self.assertEqual(fixture_hash, fixture.read_bytes())

    def test_no_heading_document_previews_and_updates_with_empty_block(self) -> None:
        with self._working_copy("no-headings.md") as target:
            status, stdout, stderr = self._run([str(target)])
            self.assertEqual((0, self._read_expected("no-headings-preview.md"), ""), (status, stdout, stderr))

            status, stdout, stderr = self._run([str(target), "--write"])
            self.assertEqual((0, "Índice actualizado.\n", ""), (status, stdout, stderr))
            self.assertEqual(self._read_expected("no-headings-preview.md"), target.read_bytes().decode("utf-8"))

    def test_error_fixtures_report_contract_diagnostic_to_stderr_and_do_not_write(self) -> None:
        references = self._load_errors()
        for fixture_name, reference in references.items():
            with self.subTest(fixture=fixture_name), self._working_copy(fixture_name) as target:
                before = target.read_bytes()
                status, stdout, stderr = self._run([str(target), "--write"])

                self.assertEqual(reference["exit_code"], status)
                self.assertEqual("", stdout)
                self.assertEqual(f"{reference['diagnostic']}\n", stderr)
                self.assertEqual(before, target.read_bytes())

    def test_invalid_resources_encoding_and_permissions_return_status_one(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            missing = directory / "missing.md"
            text = directory / "document.txt"
            text.write_text("text", encoding="utf-8")
            invalid_utf8 = directory / "invalid.md"
            invalid_utf8.write_bytes(b"\xff")
            unreadable = directory / "unreadable.md"
            unreadable.write_text("<!-- markdown-toc:start -->\n<!-- markdown-toc:end -->\n", encoding="utf-8")
            unreadable.chmod(0o000)
            read_only = directory / "read-only.md"
            original = "<!-- markdown-toc:start -->\nold\n<!-- markdown-toc:end -->\n"
            read_only.write_text(original, encoding="utf-8")
            read_only.chmod(0o444)

            cases = (
                ([str(missing)], "Error de entrada: se requiere un archivo regular.\n"),
                ([str(directory)], "Error de entrada: se requiere un archivo regular.\n"),
                ([str(text)], "Error de entrada: extensión Markdown no admitida.\n"),
                ([str(invalid_utf8)], "Error de codificación: archivo no UTF-8.\n"),
                ([str(read_only), "--write"], "Error de actualización: sin permiso de escritura.\n"),
            )
            for arguments, expected_error in cases:
                with self.subTest(arguments=arguments):
                    status, stdout, stderr = self._run(arguments)
                    self.assertEqual((1, "", expected_error), (status, stdout, stderr))
            with patch("main.stat.S_IMODE", return_value=0):
                status, stdout, stderr = self._run([str(unreadable)])
            self.assertEqual((1, "", "Error de entrada: sin permiso de lectura.\n"), (status, stdout, stderr))
            self.assertEqual(original, read_only.read_text(encoding="utf-8"))

    def test_invalid_arguments_return_usage_status_and_emit_no_traceback(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SRC / "main.py"), "--unknown"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=PROJECT_ROOT,
            check=False,
        )

        self.assertEqual(2, result.returncode)
        self.assertEqual("", result.stdout)
        self.assertIn("usage: markdown-toc", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def _run(self, arguments: list[str]) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        return run(arguments, stdout=stdout, stderr=stderr), stdout.getvalue(), stderr.getvalue()

    def _working_copy(self, fixture_name: str):
        return _WorkingCopy(self.fixtures / fixture_name)

    def _read_expected(self, name: str) -> str:
        return (self.expected / name).read_bytes().decode("utf-8")

    def _load_errors(self) -> dict[str, dict[str, object]]:
        with (self.expected / "error-scenarios.json").open(encoding="utf-8") as source:
            return json.load(source)


class _WorkingCopy:
    """Context manager that gives each integration test an isolated Markdown file."""

    def __init__(self, source: Path) -> None:
        self.source = source
        self.temporary_directory: tempfile.TemporaryDirectory[str] | None = None
        self.target: Path | None = None

    def __enter__(self) -> Path:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.target = Path(self.temporary_directory.name) / self.source.name
        self.target.write_bytes(self.source.read_bytes())
        return self.target

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        if self.temporary_directory is not None:
            self.temporary_directory.cleanup()
