"""Unit tests for phase 4 analysis and deterministic reporting."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from analyzer import analyze_batch, filter_error_events, is_error_level
from parsers import parse_file, parse_lines
from reporters import format_analysis, format_error_report, format_summary


class AnalysisTests(unittest.TestCase):
    """Verify aggregation, stable ordering, and presentation from parser output."""

    fixtures = PROJECT_ROOT / "data" / "fixtures"
    expected = PROJECT_ROOT / "data" / "expected"

    def test_fixture_aggregates_match_every_structured_reference(self) -> None:
        cases = (
            ("common-valid.log", "common", "common-valid-summary.json"),
            ("common-invalid.log", "common", "common-invalid-summary.json"),
            ("jsonl-valid.jsonl", "jsonl", "jsonl-valid-summary.json"),
            ("jsonl-invalid.jsonl", "jsonl", "jsonl-invalid-summary.json"),
        )

        for fixture_name, log_format, reference_name in cases:
            with self.subTest(fixture=fixture_name):
                result = analyze_batch(parse_file(self.fixtures / fixture_name, log_format), log_format)
                reference = self._load_reference(reference_name)
                self.assertEqual(reference["format"], result.log_format)
                self.assertEqual(reference["total_lines"], result.total_lines)
                self.assertEqual(reference["valid_events"], result.valid_events)
                self.assertEqual(reference["invalid_lines"], result.invalid_lines)
                self.assertEqual(reference["level_counts"], result.level_count_map)
                self.assertEqual(reference["top_messages"], self._messages_as_data(result))
                self.assertEqual(reference["error_line_numbers"], list(result.error_line_numbers))

    def test_top_messages_sort_by_count_then_first_physical_appearance(self) -> None:
        batch = parse_lines(
            [
                "2026-09-01T10:00:00Z INFO Segundo\n",
                "2026-09-01T10:00:01Z ERROR Primero\n",
                "2026-09-01T10:00:02Z WARNING Segundo\n",
                "2026-09-01T10:00:03Z CRITICAL Primero\n",
                "2026-09-01T10:00:04Z INFO Tercero\n",
            ],
            "common",
        )

        result = analyze_batch(batch, "common", top_limit=2)

        self.assertEqual(
            [("Segundo", 2), ("Primero", 2)],
            [(item.message, item.count) for item in result.top_messages],
        )
        self.assertEqual((2, 4), result.error_line_numbers)

    def test_empty_input_and_only_invalid_input_preserve_zero_metrics(self) -> None:
        empty = analyze_batch(parse_lines([], "common"), "common")
        invalid = analyze_batch(
            parse_lines(["\n", "2026-09-01T10:00:00Z WARN No admitido\n"], "common"),
            "common",
        )

        self.assertEqual(0, empty.total_lines)
        self.assertEqual(0, empty.valid_events)
        self.assertEqual(0, empty.invalid_lines)
        self.assertEqual([], self._messages_as_data(empty))
        self.assertEqual({"DEBUG": 0, "INFO": 0, "WARNING": 0, "ERROR": 0, "CRITICAL": 0}, empty.level_count_map)
        self.assertEqual(2, invalid.total_lines)
        self.assertEqual(0, invalid.valid_events)
        self.assertEqual(2, invalid.invalid_lines)
        self.assertEqual((), invalid.error_events)

    def test_error_threshold_accepts_only_error_and_critical(self) -> None:
        batch = parse_lines(
            [
                "2026-09-01T10:00:00Z DEBUG D\n",
                "2026-09-01T10:00:01Z INFO I\n",
                "2026-09-01T10:00:02Z WARNING W\n",
                "2026-09-01T10:00:03Z ERROR E\n",
                "2026-09-01T10:00:04Z CRITICAL C\n",
            ],
            "common",
        )

        self.assertEqual([False, False, False, True, True], [is_error_level(event.level) for event in batch.events])
        self.assertEqual((4, 5), tuple(event.line_number for event in filter_error_events(batch.events)))
        with self.assertRaises(ValueError):
            is_error_level("WARN")
        with self.assertRaises(ValueError):
            analyze_batch(batch, "unknown")  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            analyze_batch(batch, "common", top_limit=-1)

    def test_reporters_are_deterministic_and_do_not_expose_diagnostics(self) -> None:
        result = analyze_batch(parse_file(self.fixtures / "common-invalid.log", "common"), "common")

        self.assertEqual(
            "Resumen de análisis\n"
            "Ruta: data/fixtures/common-invalid.log\n"
            "Formato: common\n"
            "Líneas leídas: 6\n"
            "Eventos válidos: 2\n"
            "Líneas inválidas: 4\n"
            "Por nivel:\n"
            "- DEBUG: 0\n"
            "- INFO: 2\n"
            "- WARNING: 0\n"
            "- ERROR: 0\n"
            "- CRITICAL: 0\n"
            "Mensajes frecuentes:\n"
            "- 1 × Evento válido antes de errores\n"
            "- 1 × Evento válido después de errores",
            format_summary(result, "data/fixtures/common-invalid.log"),
        )
        self.assertEqual("Reporte de errores\nSin eventos ERROR o CRITICAL.", format_error_report(result))
        self.assertNotIn("Alias de nivel no admitido", format_summary(result, "source.log"))

        valid = analyze_batch(parse_file(self.fixtures / "common-valid.log", "common"), "common")
        combined = format_analysis(valid, "source.log", include_errors=True)
        self.assertIn("Reporte de errores\n- línea 4 | 2026-09-01T08:30:03Z | ERROR | Conexión rechazada por el proveedor", combined)
        self.assertIn("- línea 5 | 2026-09-01T08:30:04Z | CRITICAL | Servicio de pagos no disponible", combined)
        self.assertIn("- línea 6 | 2026-09-01T08:30:05Z | ERROR | Conexión rechazada por el proveedor", combined)
        self.assertEqual(format_summary(valid, "source.log"), format_analysis(valid, "source.log"))

    @staticmethod
    def _messages_as_data(result: object) -> list[dict[str, object]]:
        return [
            {"message": item.message, "count": item.count}
            for item in result.top_messages  # type: ignore[union-attr]
        ]

    def _load_reference(self, name: str) -> dict[str, object]:
        with (self.expected / name).open(encoding="utf-8") as source:
            return json.load(source)


if __name__ == "__main__":
    unittest.main()
