"""Unit tests for the phase 3 sequential log parsers."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from models import DiagnosticCode, InputReadError
from parsers import (
    get_line_parser,
    is_iso8601_timestamp,
    iter_parse_lines,
    parse_common_line,
    parse_file,
    parse_jsonl_line,
    parse_lines,
)


class SequentialParserTests(unittest.TestCase):
    """Verify contract-v1 normalization and per-line diagnostics."""

    fixtures = PROJECT_ROOT / "data" / "fixtures"
    expected = PROJECT_ROOT / "data" / "expected"

    def test_common_fixture_normalizes_all_valid_events_in_order(self) -> None:
        batch = parse_file(self.fixtures / "common-valid.log", "common")
        reference = self._load_reference("common-valid-summary.json")

        self.assertEqual(reference["valid_events"], len(batch.events))
        self.assertEqual((), batch.diagnostics)
        self.assertEqual(list(range(1, 8)), [event.line_number for event in batch.events])
        self.assertEqual(
            ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "ERROR", "INFO"],
            [event.level for event in batch.events],
        )
        self.assertEqual("Usuario José inició sesión", batch.events[-1].message)
        self.assertEqual({}, dict(batch.events[0].metadata))

    def test_common_invalid_fixture_preserves_valid_lines_and_classifies_diagnostics(self) -> None:
        batch = parse_file(self.fixtures / "common-invalid.log", "common")
        reference = self._load_reference("common-invalid-summary.json")

        self.assertEqual(reference["valid_events"], len(batch.events))
        self.assertEqual(reference["invalid_lines"], len(batch.diagnostics))
        self.assertEqual([2, 6], [event.line_number for event in batch.events])
        self.assertEqual([1, 3, 4, 5], [item.line_number for item in batch.diagnostics])
        self.assertEqual(
            [
                DiagnosticCode.BLANK_LINE,
                DiagnosticCode.INVALID_LEVEL,
                DiagnosticCode.COMMON_STRUCTURE,
                DiagnosticCode.INVALID_TIMESTAMP,
            ],
            [item.code for item in batch.diagnostics],
        )

    def test_jsonl_fixture_normalizes_metadata_and_case_insensitive_levels(self) -> None:
        batch = parse_file(self.fixtures / "jsonl-valid.jsonl", "jsonl")
        reference = self._load_reference("jsonl-valid-summary.json")

        self.assertEqual(reference["valid_events"], len(batch.events))
        self.assertEqual((), batch.diagnostics)
        self.assertEqual([1, 2, 3, 4, 5, 6], [event.line_number for event in batch.events])
        self.assertEqual(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "ERROR"], [event.level for event in batch.events])
        self.assertEqual({"service": "worker"}, dict(batch.events[0].metadata))
        self.assertEqual("Pérdida de conexión con clúster", batch.events[4].message)

    def test_jsonl_invalid_fixture_emits_one_diagnostic_per_invalid_line(self) -> None:
        batch = parse_file(self.fixtures / "jsonl-invalid.jsonl", "jsonl")
        reference = self._load_reference("jsonl-invalid-summary.json")

        self.assertEqual(reference["valid_events"], len(batch.events))
        self.assertEqual(reference["invalid_lines"], len(batch.diagnostics))
        self.assertEqual([1, 8], [event.line_number for event in batch.events])
        self.assertEqual([2, 3, 4, 5, 6, 7], [item.line_number for item in batch.diagnostics])
        self.assertEqual(
            [
                DiagnosticCode.INVALID_JSON,
                DiagnosticCode.INVALID_LEVEL,
                DiagnosticCode.MISSING_FIELD,
                DiagnosticCode.EMPTY_FIELD,
                DiagnosticCode.JSON_NOT_OBJECT,
                DiagnosticCode.BLANK_LINE,
            ],
            [item.code for item in batch.diagnostics],
        )
        self.assertTrue(batch.diagnostics[0].detail.startswith("posición "))

    def test_empty_input_has_no_results_while_blank_line_has_a_diagnostic(self) -> None:
        self.assertEqual((), parse_file(self.fixtures / "empty.log", "common").results)
        blank = parse_lines(["   \n"], "jsonl")
        self.assertEqual(1, len(blank.diagnostics))
        self.assertEqual(DiagnosticCode.BLANK_LINE, blank.diagnostics[0].code)

    def test_common_parser_accepts_tab_separator_and_no_final_newline(self) -> None:
        batch = parse_lines(["2026-09-01T08:30:00+02:00\tinfo\tMensaje final"], "common")

        self.assertEqual(1, len(batch.events))
        event = batch.events[0]
        self.assertEqual("INFO", event.level)
        self.assertEqual("Mensaje final", event.message)
        self.assertEqual("2026-09-01T08:30:00+02:00", event.timestamp)

    def test_jsonl_rejects_invalid_required_field_types_and_timestamps(self) -> None:
        type_result = parse_jsonl_line(
            '{"timestamp": 1, "level": "INFO", "message": "Texto"}', 1
        )
        timestamp_result = parse_jsonl_line(
            '{"timestamp": "ayer", "level": "INFO", "message": "Texto"}', 2
        )

        self.assertEqual(DiagnosticCode.INVALID_FIELD_TYPE, type_result.diagnostic.code)
        self.assertEqual("timestamp", type_result.diagnostic.detail)
        self.assertEqual(DiagnosticCode.INVALID_TIMESTAMP, timestamp_result.diagnostic.code)

    def test_common_parser_rejects_missing_message_and_unknown_level(self) -> None:
        missing = parse_common_line("2026-09-01T08:30:00Z ERROR", 1)
        unknown = parse_common_line("2026-09-01T08:30:00Z WARN No admitido", 2)

        self.assertEqual(DiagnosticCode.COMMON_STRUCTURE, missing.diagnostic.code)
        self.assertEqual(DiagnosticCode.INVALID_LEVEL, unknown.diagnostic.code)
        self.assertEqual("WARN", unknown.diagnostic.detail)

    def test_timestamp_validation_is_strict_and_supports_z_or_numeric_offset(self) -> None:
        self.assertTrue(is_iso8601_timestamp("2026-09-01T08:30:00Z"))
        self.assertTrue(is_iso8601_timestamp("2026-09-01T08:30:00+02:00"))
        self.assertFalse(is_iso8601_timestamp("2026-09-01 08:30:00"))
        self.assertFalse(is_iso8601_timestamp("marca-sin-formato"))
        self.assertFalse(is_iso8601_timestamp(""))

    def test_iterable_is_consumed_sequentially_and_unknown_format_is_rejected(self) -> None:
        seen: list[str] = []

        def lines() -> object:
            for line in [
                "2026-09-01T08:30:00Z INFO Primero\n",
                "2026-09-01T08:30:01Z ERROR Segundo\n",
            ]:
                seen.append(line)
                yield line

        results = list(iter_parse_lines(lines(), "common"))
        self.assertEqual(2, len(results))
        self.assertEqual(2, len(seen))
        with self.assertRaises(ValueError):
            get_line_parser("unknown")  # type: ignore[arg-type]

    def test_parse_file_wraps_utf8_decode_errors(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            source = Path(temporary_directory) / "invalid-utf8.log"
            source.write_bytes(b"\xff\xfe")
            with self.assertRaises(InputReadError) as raised:
                parse_file(source, "common")

        self.assertIsInstance(raised.exception.__cause__, UnicodeDecodeError)

    def _load_reference(self, name: str) -> dict[str, object]:
        with (self.expected / name).open(encoding="utf-8") as source:
            return json.load(source)


if __name__ == "__main__":
    unittest.main()
