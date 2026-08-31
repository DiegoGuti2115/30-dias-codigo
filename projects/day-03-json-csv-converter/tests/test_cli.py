"""Integration tests for the JSON and CSV command-line interface."""

from __future__ import annotations

import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIRECTORY = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIRECTORY))

from main import main, parse_arguments


class CliTests(unittest.TestCase):
    """Verify commands, safe output handling, and process-level execution."""

    def test_parser_exposes_both_operations(self) -> None:
        arguments = parse_arguments(["json-to-csv", "input.json", "output.csv"])
        self.assertEqual("json-to-csv", arguments.command)
        self.assertFalse(arguments.overwrite)

        arguments = parse_arguments(["csv-to-json", "input.csv", "output.json", "--overwrite"])
        self.assertEqual("csv-to-json", arguments.command)
        self.assertTrue(arguments.overwrite)

    def test_cli_converts_both_directions_and_requires_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            json_input = root / "input.json"
            csv_output = root / "output.csv"
            json_output = root / "roundtrip.json"
            json_input.write_text('[{"id": 1, "name": "Ana"}]', encoding="utf-8")

            output = io.StringIO()
            self.assertEqual(0, main(["json-to-csv", str(json_input), str(csv_output)], output))
            self.assertTrue(csv_output.exists())
            self.assertIn("1 registro", output.getvalue())

            self.assertEqual(0, main(["csv-to-json", str(csv_output), str(json_output)], io.StringIO()))
            self.assertEqual(
                [{"id": "1", "name": "Ana"}],
                json.loads(json_output.read_text(encoding="utf-8")),
            )

            self.assertEqual(2, main(["json-to-csv", str(json_input), str(csv_output)], io.StringIO()))
            self.assertEqual(
                0,
                main(
                    ["json-to-csv", str(json_input), str(csv_output), "--overwrite"],
                    io.StringIO(),
                ),
            )

    def test_cli_rejects_wrong_extensions_and_invalid_json_without_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            invalid = root / "invalid.json"
            output = root / "result.csv"
            invalid.write_text("{invalid", encoding="utf-8")

            self.assertEqual(2, main(["json-to-csv", str(invalid), str(output)], io.StringIO()))
            self.assertFalse(output.exists())
            self.assertEqual(2, main(["json-to-csv", str(invalid), str(root / "result.txt")], io.StringIO()))

    def test_script_entrypoint_runs_in_a_clean_python_process(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "input.csv"
            target = root / "output.json"
            source.write_text("id,name\n7,Lucía\n", encoding="utf-8", newline="")

            result = subprocess.run(
                [sys.executable, str(SRC_DIRECTORY / "main.py"), "csv-to-json", str(source), str(target)],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("Conversión completada", result.stdout)
            self.assertEqual([{"id": "7", "name": "Lucía"}], json.loads(target.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
