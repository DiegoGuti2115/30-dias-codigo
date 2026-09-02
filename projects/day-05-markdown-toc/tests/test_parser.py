"""Unit tests for Phase 3 Markdown interpretation."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from parser import Heading, parse_lines, parse_markdown


class MarkdownParserTests(unittest.TestCase):
    """Verify the contract-v1 ATX grammar and fenced-code exclusion."""

    fixtures = PROJECT_ROOT / "data" / "fixtures"
    expected = PROJECT_ROOT / "data" / "expected"

    def test_complex_fixture_extracts_only_eligible_headings_in_physical_order(self) -> None:
        reference = self._load_reference("complex-valid.json")
        result = parse_markdown(self._read_fixture("complex-valid.md"))

        self.assertEqual(
            [(item["line"], item["level"], item["text"]) for item in reference["headings"]],
            [(heading.line, heading.level, heading.text) for heading in result.headings],
        )
        self.assertIsNone(result.excluded_from_line)

    def test_atx_edge_fixture_ignores_invalid_forms_and_removes_closing_hashes(self) -> None:
        reference = self._load_reference("atx-edge-cases.json")
        result = parse_markdown(self._read_fixture("atx-edge-cases.md"))

        self.assertEqual(
            [(item["line"], item["level"], item["text"]) for item in reference["headings"]],
            [(heading.line, heading.level, heading.text) for heading in result.headings],
        )

    def test_unclosed_fence_excludes_all_remaining_lines(self) -> None:
        reference = self._load_reference("fenced-code-unclosed.json")
        result = parse_markdown(self._read_fixture("fenced-code-unclosed.md"))

        self.assertEqual(reference["excluded_from_line"], result.excluded_from_line)
        self.assertEqual(
            [(item["line"], item["level"], item["text"]) for item in reference["headings"]],
            [(heading.line, heading.level, heading.text) for heading in result.headings],
        )

    def test_setext_headings_are_not_part_of_v1(self) -> None:
        result = parse_markdown("Título Setext\n=============\n# Encabezado ATX\n")

        self.assertEqual((Heading(line=3, level=1, text="Encabezado ATX"),), result.headings)

    def test_opening_and_closing_fences_obey_character_and_minimum_length(self) -> None:
        result = parse_markdown(
            "# Visible\n"
            "```python\n"
            "## Excluido\n"
            "``\n"
            "### Sigue excluido\n"
            "````\n"
            "## Visible de nuevo\n"
        )

        self.assertEqual(
            (
                Heading(line=1, level=1, text="Visible"),
                Heading(line=7, level=2, text="Visible de nuevo"),
            ),
            result.headings,
        )
        self.assertIsNone(result.excluded_from_line)

    def test_empty_and_headingless_documents_return_no_headings(self) -> None:
        self.assertEqual((), parse_markdown(self._read_fixture("empty.md")).headings)
        self.assertEqual((), parse_markdown(self._read_fixture("no-headings.md")).headings)

    def test_parse_lines_matches_text_parsing(self) -> None:
        document = "# Uno\n\n## Dos\n"
        self.assertEqual(parse_markdown(document), parse_lines(document.splitlines(keepends=True)))

    def _read_fixture(self, name: str) -> str:
        return (self.fixtures / name).read_text(encoding="utf-8")

    def _load_reference(self, name: str) -> dict[str, object]:
        with (self.expected / name).open(encoding="utf-8") as source:
            return json.load(source)


if __name__ == "__main__":
    unittest.main()
