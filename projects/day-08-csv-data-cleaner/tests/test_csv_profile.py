from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from csv_profile import CsvContractError, load_csv, profile_csv


FIXTURES = PROJECT_ROOT / "data" / "fixtures"


class CsvLoadingTests(unittest.TestCase):
    def test_loads_utf8_bom_and_profiles_happy_fixture(self) -> None:
        dataset = load_csv(FIXTURES / "happy-input.csv")

        self.assertEqual(dataset.headers, (" Display Name ", "status", "comment"))
        self.assertEqual(dataset.data_row_count, 5)
        self.assertEqual(dataset.column_count, 3)
        self.assertEqual(profile_csv(dataset.headers, dataset.rows).as_dict(), {
            "headers": [" Display Name ", "status", "comment"],
            "empty_value_count": 4,
            "empty_row_count": 1,
            "exact_duplicate_row_count": 0,
            "formula_like_cell_count": 1,
        })

    def test_semicolon_text_is_one_valid_comma_dialect_field(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "semicolon-is-text.csv"
            source.write_text("label;status\nalpha;ready\n", encoding="utf-8")

            dataset = load_csv(source)

        self.assertEqual(dataset.headers, ("label;status",))
        self.assertEqual(dataset.rows, (("alpha;ready",),))

    def test_rejects_contractual_csv_failures(self) -> None:
        cases = {
            "empty-input.csv": "csv_missing_header",
            "irregular-input.csv": "csv_irregular_row",
            "malformed-input.csv": "csv_malformed",
            "invalid-utf8-input.csv": "csv_invalid_encoding",
        }
        for fixture, code in cases.items():
            with self.subTest(fixture=fixture):
                with self.assertRaisesRegex(CsvContractError, code):
                    load_csv(FIXTURES / fixture)

    def test_rejects_empty_and_duplicate_headers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "invalid-headers.csv"
            source.write_text("label,label\na,b\n", encoding="utf-8")
            with self.assertRaisesRegex(CsvContractError, "csv_invalid_headers"):
                load_csv(source)
