"""End-to-end regression coverage for the final quality phase."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
FIXTURES = PROJECT_ROOT / "data" / "fixtures"
EXPECTED = PROJECT_ROOT / "data" / "expected"


class QualityRegressionTests(unittest.TestCase):
    """Exercise the public command with relative and absolute local paths."""

    def test_relative_preview_matches_reference_without_mutating_document(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            working_directory = Path(temporary_directory)
            target = working_directory / "guide.md"
            target.write_bytes((FIXTURES / "complex-valid.md").read_bytes())
            before = target.read_bytes()

            result = self._command("guide.md", cwd=working_directory)

            self.assertEqual(0, result.returncode)
            self.assertEqual((EXPECTED / "complex-valid-preview.md").read_text(encoding="utf-8"), result.stdout)
            self.assertEqual("", result.stderr)
            self.assertEqual(before, target.read_bytes())

    def test_absolute_write_preserves_bom_crlf_unicode_and_is_idempotent(self) -> None:
        original = (
            b"\xef\xbb\xbf# Caf\xc3\xa9\r\n\r\n"
            b"<!-- markdown-toc:start -->\r\n"
            b"obsolete\r\n"
            b"<!-- markdown-toc:end -->\r\n"
            b"\r\nFin \xe2\x9c\x93\r\n"
        )
        expected = (
            b"\xef\xbb\xbf# Caf\xc3\xa9\r\n\r\n"
            b"<!-- markdown-toc:start -->\r\n"
            b"- [Caf\xc3\xa9](#cafe)\r\n"
            b"<!-- markdown-toc:end -->\r\n"
            b"\r\nFin \xe2\x9c\x93\r\n"
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            target = Path(temporary_directory) / "unicode.markdown"
            target.write_bytes(original)

            first = self._command(str(target), "--write", cwd=PROJECT_ROOT)
            second = self._command(str(target), "--write", cwd=PROJECT_ROOT)

            self.assertEqual((0, "Índice actualizado.\n", ""), (first.returncode, first.stdout, first.stderr))
            self.assertEqual((0, "Índice actualizado.\n", ""), (second.returncode, second.stdout, second.stderr))
            self.assertEqual(expected, target.read_bytes())

    @staticmethod
    def _command(*arguments: str, cwd: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SRC / "main.py"), *arguments],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=cwd,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            check=False,
        )
