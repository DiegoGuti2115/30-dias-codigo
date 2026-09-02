"""Unit tests for Phase 4 protected TOC-block replacement."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from parser import parse_markdown
from rewriter import RewriteError, build_preview, locate_block, update_file
from toc import build_entries, render_toc


class RewriterTests(unittest.TestCase):
    """Verify validation, preservation, preview, and atomic persistence."""

    fixtures = PROJECT_ROOT / "data" / "fixtures"
    expected = PROJECT_ROOT / "data" / "expected"

    def test_complex_preview_matches_reference_and_preserves_exterior(self) -> None:
        document = self._read_fixture("complex-valid.md")
        proposed = build_preview(document, self._toc_for(document))

        self.assertEqual(self._read_expected("complex-valid-preview.md"), proposed)
        region = locate_block(document)
        self.assertEqual(document[: region.content_start], proposed[: region.content_start])
        self.assertEqual(document[region.content_end :], proposed[-len(document[region.content_end :]) :])

    def test_headingless_preview_removes_only_the_obsolete_interior(self) -> None:
        document = self._read_fixture("no-headings.md")

        self.assertEqual(self._read_expected("no-headings-preview.md"), build_preview(document, ""))

    def test_invalid_blocks_match_contract_diagnostics_without_producing_a_preview(self) -> None:
        references = self._load_errors()
        for fixture_name, reference in references.items():
            with self.subTest(fixture=fixture_name):
                with self.assertRaisesRegex(RewriteError, f"^{reference['diagnostic']}$"):
                    build_preview(self._read_fixture(fixture_name), "- [No importa](#no-importa)")

    def test_marker_with_extra_text_is_invalid(self) -> None:
        document = "<!-- markdown-toc:start --> extra\n<!-- markdown-toc:end -->\n"

        with self.assertRaisesRegex(RewriteError, "^Bloque de índice inválido\\.$"):
            locate_block(document)

    def test_preview_preserves_mixed_newlines_exterior_and_uses_first_newline_for_toc(self) -> None:
        document = (
            "Antes\r\n"
            "<!-- markdown-toc:start -->\n"
            "Viejo\r\n"
            "<!-- markdown-toc:end -->\r"
            "Después"
        )

        self.assertEqual(
            "Antes\r\n"
            "<!-- markdown-toc:start -->\n"
            "- [Uno](#uno)\r\n"
            "  - [Dos](#dos)\r\n"
            "<!-- markdown-toc:end -->\r"
            "Después",
            build_preview(document, "- [Uno](#uno)\n  - [Dos](#dos)"),
        )

    def test_update_is_idempotent_and_does_not_modify_source_fixture(self) -> None:
        fixture = self.fixtures / "complex-valid.md"
        original_fixture = fixture.read_bytes()
        with tempfile.TemporaryDirectory() as temporary_directory:
            target = Path(temporary_directory) / "document.md"
            target.write_bytes(original_fixture)
            toc = self._toc_for(target.read_text(encoding="utf-8"))

            first = update_file(target, toc)
            after_first = target.read_bytes()
            second = update_file(target, toc)

            self.assertTrue(first.changed)
            self.assertFalse(second.changed)
            self.assertEqual(after_first, target.read_bytes())
            self.assertEqual(self._read_expected("complex-valid-preview.md"), target.read_text(encoding="utf-8"))
        self.assertEqual(original_fixture, fixture.read_bytes())

    def test_update_preserves_bom_final_newline_policy_and_original_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            target = Path(temporary_directory) / "bom.markdown"
            target.write_bytes(
                b"\xef\xbb\xbf# Titulo\r\n<!-- markdown-toc:start -->\r\nold\r\n<!-- markdown-toc:end -->"
            )
            target.chmod(0o640)

            result = update_file(target, "- [Titulo](#titulo)")

            self.assertTrue(result.changed)
            self.assertEqual(
                b"\xef\xbb\xbf# Titulo\r\n<!-- markdown-toc:start -->\r\n- [Titulo](#titulo)\r\n<!-- markdown-toc:end -->",
                target.read_bytes(),
            )
            self.assertTrue(target.is_file())

    def test_write_failures_leave_original_and_no_temporary_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            target = directory / "document.md"
            original = b"# Uno\n<!-- markdown-toc:start -->\nviejo\n<!-- markdown-toc:end -->\n"
            target.write_bytes(original)

            with patch("rewriter.os.replace", side_effect=OSError("fallo simulado")):
                with self.assertRaisesRegex(RewriteError, "^Error de actualización: no se pudo persistir el archivo\\.$"):
                    update_file(target, "- [Uno](#uno)")

            self.assertEqual(original, target.read_bytes())
            self.assertEqual([], list(directory.glob(f".{target.name}.*")))

    def test_rejects_unsupported_resources_and_read_only_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            not_markdown = directory / "document.txt"
            not_markdown.write_text("texto", encoding="utf-8")
            read_only = directory / "read-only.md"
            original = "<!-- markdown-toc:start -->\nold\n<!-- markdown-toc:end -->\n"
            read_only.write_text(original, encoding="utf-8")
            read_only.chmod(0o444)

            with self.assertRaisesRegex(RewriteError, "^Error de entrada: extensión Markdown no admitida\\.$"):
                update_file(not_markdown, "")
            with self.assertRaisesRegex(RewriteError, "^Error de entrada: se requiere un archivo regular\\.$"):
                update_file(directory, "")
            with self.assertRaisesRegex(RewriteError, "^Error de actualización: sin permiso de escritura\\.$"):
                update_file(read_only, "")
            self.assertEqual(original, read_only.read_text(encoding="utf-8"))

    def test_rejects_invalid_utf8_without_modifying_the_document(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            target = Path(temporary_directory) / "invalid.md"
            original = b"<!-- markdown-toc:start -->\n\xff\n<!-- markdown-toc:end -->\n"
            target.write_bytes(original)

            with self.assertRaisesRegex(RewriteError, "^Error de codificación: archivo no UTF-8\\.$"):
                update_file(target, "")

            self.assertEqual(original, target.read_bytes())

    def _toc_for(self, document: str) -> str:
        return render_toc(build_entries(parse_markdown(document).headings))

    def _read_fixture(self, name: str) -> str:
        return (self.fixtures / name).read_text(encoding="utf-8")

    def _read_expected(self, name: str) -> str:
        return (self.expected / name).read_text(encoding="utf-8")

    def _load_errors(self) -> dict[str, dict[str, object]]:
        with (self.expected / "error-scenarios.json").open(encoding="utf-8") as source:
            return json.load(source)


if __name__ == "__main__":
    unittest.main()
