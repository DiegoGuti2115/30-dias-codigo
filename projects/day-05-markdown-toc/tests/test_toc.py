"""Unit tests for Phase 3 anchors and hierarchical TOC rendering."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from parser import Heading, parse_markdown
from toc import build_entries, normalize_anchor, render_toc


class TocTests(unittest.TestCase):
    """Verify deterministic anchors, duplicate suffixes, and presentation depth."""

    fixtures = PROJECT_ROOT / "data" / "fixtures"
    expected = PROJECT_ROOT / "data" / "expected"

    def test_complex_fixture_matches_all_reference_entries_and_rendered_toc(self) -> None:
        reference = self._load_reference("complex-valid.json")
        headings = parse_markdown(self._read_fixture("complex-valid.md")).headings
        entries = build_entries(headings)

        self.assertEqual(reference["headings"], [self._entry_as_data(entry) for entry in entries])
        self.assertEqual(reference["toc"], render_toc(entries))

    def test_atx_edge_fixture_matches_reference_anchors_and_depths(self) -> None:
        reference = self._load_reference("atx-edge-cases.json")
        headings = parse_markdown(self._read_fixture("atx-edge-cases.md")).headings
        entries = build_entries(headings)

        self.assertEqual(reference["headings"], [self._entry_as_data(entry) for entry in entries])
        self.assertEqual(reference["toc"], render_toc(entries))

    def test_unclosed_fence_and_headingless_documents_have_stable_outputs(self) -> None:
        fenced_reference = self._load_reference("fenced-code-unclosed.json")
        fenced_entries = build_entries(parse_markdown(self._read_fixture("fenced-code-unclosed.md")).headings)

        self.assertEqual(fenced_reference["headings"], [self._entry_as_data(entry) for entry in fenced_entries])
        self.assertEqual(fenced_reference["toc"], render_toc(fenced_entries))
        self.assertEqual("", render_toc(build_entries(parse_markdown(self._read_fixture("no-headings.md")).headings)))
        self.assertEqual("", render_toc(build_entries(parse_markdown(self._read_fixture("empty.md")).headings)))

    def test_normalize_anchor_follows_unicode_punctuation_and_fallback_rules(self) -> None:
        self.assertEqual("guia-cafe-te", normalize_anchor("Guía: Café & Té!"))
        self.assertEqual("enlacehttpsejemplotest-y-codigo", normalize_anchor("[Enlace](https://ejemplo.test) y `código`"))
        self.assertEqual("seccion", normalize_anchor("!!!"))
        self.assertEqual("alpha-beta", normalize_anchor("--Alpha\t  Beta---"))

    def test_duplicate_bases_are_counted_in_physical_order_across_levels(self) -> None:
        entries = build_entries(
            (
                Heading(line=1, level=1, text="Repetido"),
                Heading(line=2, level=3, text="Repetido"),
                Heading(line=3, level=2, text="Repetido"),
            )
        )

        self.assertEqual(["repetido", "repetido-2", "repetido-3"], [entry.anchor for entry in entries])
        self.assertEqual([0, 1, 0], [entry.depth for entry in entries])

    def test_level_jumps_create_no_empty_depths_and_descend_to_nearest_ancestor(self) -> None:
        entries = build_entries(
            (
                Heading(line=1, level=2, text="Base"),
                Heading(line=2, level=5, text="Salto"),
                Heading(line=3, level=6, text="Más profundo"),
                Heading(line=4, level=3, text="Retroceso sin ancestro"),
                Heading(line=5, level=4, text="Hijo"),
                Heading(line=6, level=2, text="Misma raíz"),
            )
        )

        self.assertEqual([0, 1, 2, 0, 1, 0], [entry.depth for entry in entries])
        self.assertEqual(
            "- [Base](#base)\n"
            "  - [Salto](#salto)\n"
            "    - [Más profundo](#mas-profundo)\n"
            "- [Retroceso sin ancestro](#retroceso-sin-ancestro)\n"
            "  - [Hijo](#hijo)\n"
            "- [Misma raíz](#misma-raiz)",
            render_toc(entries),
        )

    def _read_fixture(self, name: str) -> str:
        return (self.fixtures / name).read_text(encoding="utf-8")

    def _load_reference(self, name: str) -> dict[str, object]:
        with (self.expected / name).open(encoding="utf-8") as source:
            return json.load(source)

    @staticmethod
    def _entry_as_data(entry: object) -> dict[str, object]:
        return {
            "line": entry.line,  # type: ignore[union-attr]
            "level": entry.level,  # type: ignore[union-attr]
            "text": entry.text,  # type: ignore[union-attr]
            "anchor": entry.anchor,  # type: ignore[union-attr]
            "depth": entry.depth,  # type: ignore[union-attr]
        }


if __name__ == "__main__":
    unittest.main()
