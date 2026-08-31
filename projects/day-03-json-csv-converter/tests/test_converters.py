"""Unit tests for JSON and CSV conversion services."""

from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from converters import (
    collect_headers,
    load_csv_records,
    load_json_records,
    write_csv_to_json,
    write_json_to_csv,
)
from validators import ConversionError


class ConverterTests(unittest.TestCase):
    """Verify supported transformations and strict format validation."""

    def test_json_to_csv_keeps_first_seen_headers_and_handles_special_cells(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "records.json"
            target = root / "records.csv"
            source.write_text(
                json.dumps(
                    [
                        {"id": 1, "name": "Ana, Pérez", "active": True},
                        {"id": 2, "note": "Primera línea\nSegunda línea", "active": None},
                    ]
                ),
                encoding="utf-8",
            )

            records = load_json_records(source)
            self.assertEqual(["id", "name", "active", "note"], collect_headers(records))
            self.assertEqual(2, write_json_to_csv(records, target))

            with target.open("r", encoding="utf-8", newline="") as converted:
                rows = list(csv.DictReader(converted))
            self.assertEqual("Ana, Pérez", rows[0]["name"])
            self.assertEqual("true", rows[0]["active"])
            self.assertEqual("", rows[1]["name"])
            self.assertEqual("", rows[1]["active"])
            self.assertEqual("Primera línea\nSegunda línea", rows[1]["note"])

    def test_csv_to_json_preserves_all_values_as_text(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "records.csv"
            target = root / "records.json"
            source.write_text(
                "code,enabled,reference,comment\n0012,true,2026-09-01,\"Hola, mundo\"\n",
                encoding="utf-8",
                newline="",
            )

            headers, records = load_csv_records(source)
            self.assertEqual(["code", "enabled", "reference", "comment"], headers)
            self.assertEqual(1, write_csv_to_json(records, target))
            converted = json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(
                [{"code": "0012", "enabled": "true", "reference": "2026-09-01", "comment": "Hola, mundo"}],
                converted,
            )
            self.assertTrue(all(isinstance(value, str) for value in converted[0].values()))

    def test_json_rejects_empty_root_non_objects_and_nested_structures(self) -> None:
        cases = {
            "empty": [],
            "object": {"id": 1},
            "non_object_item": ["record"],
            "nested_object": [{"id": 1, "meta": {"zone": "EU"}}],
            "nested_list": [{"id": 1, "tags": ["a"]}],
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            for name, payload in cases.items():
                source = root / f"{name}.json"
                source.write_text(json.dumps(payload), encoding="utf-8")
                with self.subTest(case=name), self.assertRaises(ConversionError):
                    load_json_records(source)

    def test_csv_rejects_missing_or_duplicate_headers_and_extra_fields(self) -> None:
        cases = {
            "empty.csv": "",
            "blank.csv": ",name\n1,Ana\n",
            "duplicate.csv": "id,id\n1,2\n",
            "extra.csv": "id,name\n1,Ana,extra\n",
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            for name, content in cases.items():
                source = root / name
                source.write_text(content, encoding="utf-8", newline="")
                with self.subTest(case=name), self.assertRaises(ConversionError):
                    load_csv_records(source)


if __name__ == "__main__":
    unittest.main()
