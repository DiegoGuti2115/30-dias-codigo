"""Integration tests for the v1 command-line log analyzer."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MAIN_SCRIPT = PROJECT_ROOT / "src" / "main.py"
FIXTURES = PROJECT_ROOT / "data" / "fixtures"


class CommandLineTests(unittest.TestCase):
    """Verify documented CLI arguments, output, and process exit codes."""

    def test_common_fixture_prints_summary_and_error_report_in_input_order(self) -> None:
        completed = self._run(
            "analyze",
            str(FIXTURES / "common-valid.log"),
            "--format",
            "common",
            "--errors",
        )

        self.assertEqual(0, completed.returncode)
        self.assertEqual("", completed.stderr)
        self.assertIn("Resumen de análisis", completed.stdout)
        self.assertIn("Formato: common", completed.stdout)
        self.assertIn("Eventos válidos: 7", completed.stdout)
        self.assertIn("Líneas inválidas: 0", completed.stdout)
        self.assertIn("- ERROR: 2", completed.stdout)
        self.assertIn("- CRITICAL: 1", completed.stdout)
        self.assertIn("- 2 × Conexión rechazada por el proveedor", completed.stdout)
        self.assertIn("Reporte de errores", completed.stdout)
        error = completed.stdout.index("línea 4 | 2026-09-01T08:30:03Z | ERROR")
        critical = completed.stdout.index("línea 5 | 2026-09-01T08:30:04Z | CRITICAL")
        repeated = completed.stdout.index("línea 6 | 2026-09-01T08:30:05Z | ERROR")
        self.assertLess(error, critical)
        self.assertLess(critical, repeated)

    def test_jsonl_fixture_accepts_metadata_and_summary_only_without_errors_flag(self) -> None:
        completed = self._run(
            "analyze",
            str(FIXTURES / "jsonl-valid.jsonl"),
            "--format",
            "jsonl",
        )

        self.assertEqual(0, completed.returncode)
        self.assertEqual("", completed.stderr)
        self.assertIn("Formato: jsonl", completed.stdout)
        self.assertIn("Eventos válidos: 6", completed.stdout)
        self.assertIn("- 2 × Tiempo de espera agotado", completed.stdout)
        self.assertNotIn("Reporte de errores", completed.stdout)
        self.assertNotIn("request_id", completed.stdout)

    def test_invalid_lines_do_not_fail_a_valid_analysis_or_expose_their_content(self) -> None:
        completed = self._run(
            "analyze",
            str(FIXTURES / "common-invalid.log"),
            "--format",
            "common",
            "--errors",
        )

        self.assertEqual(0, completed.returncode)
        self.assertEqual("", completed.stderr)
        self.assertIn("Eventos válidos: 2", completed.stdout)
        self.assertIn("Líneas inválidas: 4", completed.stdout)
        self.assertIn("Sin eventos ERROR o CRITICAL.", completed.stdout)
        self.assertNotIn("Alias de nivel no admitido", completed.stdout)
        self.assertNotIn("Timestamp inválido", completed.stdout)

    def test_empty_or_all_invalid_files_return_analysis_error_without_summary(self) -> None:
        for fixture_name in ("empty.log", "common-all-invalid.log"):
            with self.subTest(fixture=fixture_name):
                completed = self._run(
                    "analyze",
                    str(FIXTURES / fixture_name),
                    "--format",
                    "common",
                )
                self.assertEqual(1, completed.returncode)
                self.assertEqual("", completed.stdout)
                self.assertIn("Error de análisis: el archivo no contiene eventos válidos.", completed.stderr)

    def test_nonexistent_path_directory_and_invalid_utf8_return_input_error(self) -> None:
        missing = self._run(
            "analyze",
            str(FIXTURES / "missing.log"),
            "--format",
            "common",
        )
        directory = self._run(
            "analyze",
            str(FIXTURES),
            "--format",
            "common",
        )

        self.assertEqual(1, missing.returncode)
        self.assertEqual("", missing.stdout)
        self.assertIn("Error de entrada: la ruta no existe:", missing.stderr)
        self.assertEqual(1, directory.returncode)
        self.assertEqual("", directory.stdout)
        self.assertIn("Error de entrada: la ruta no es un archivo:", directory.stderr)

        with tempfile.TemporaryDirectory() as temporary_directory:
            invalid_utf8 = Path(temporary_directory) / "invalid-utf8.log"
            invalid_utf8.write_bytes(b"\xff\xfe")
            undecodable = self._run(
                "analyze",
                str(invalid_utf8),
                "--format",
                "common",
            )

        self.assertEqual(1, undecodable.returncode)
        self.assertEqual("", undecodable.stdout)
        self.assertIn("Error de entrada: no se pudo leer como UTF-8:", undecodable.stderr)
        self.assertNotIn("Traceback", undecodable.stderr)

    def test_missing_or_invalid_arguments_return_argparse_usage_error(self) -> None:
        missing_command = self._run()
        missing_format = self._run("analyze", str(FIXTURES / "common-valid.log"))
        invalid_format = self._run(
            "analyze",
            str(FIXTURES / "common-valid.log"),
            "--format",
            "unknown",
        )

        for completed in (missing_command, missing_format, invalid_format):
            with self.subTest(arguments=completed.args):
                self.assertEqual(2, completed.returncode)
                self.assertEqual("", completed.stdout)
                self.assertIn("usage:", completed.stderr.lower())

    @staticmethod
    def _run(*arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(MAIN_SCRIPT), *arguments],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict",
            check=False,
        )


if __name__ == "__main__":
    unittest.main()
