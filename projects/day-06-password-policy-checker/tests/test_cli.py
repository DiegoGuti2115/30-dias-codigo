"""Integration tests for the v1 CLI and its secret-safe presentation."""

from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from main import (
    PROMPT,
    SECURE_INPUT_ERROR,
    UNEXPECTED_ERROR,
    USAGE,
    run,
)


class CommandLineTests(unittest.TestCase):
    """Verify statuses, channels, and non-disclosure at the CLI boundary."""

    def test_valid_evaluation_has_stable_safe_output_and_status_zero(self) -> None:
        candidate = self._valid_candidate()

        status, stdout, stderr = self._run(["check"], lambda prompt: candidate)

        self.assertEqual(0, status)
        self.assertEqual("Contraseña válida según la política v1.\n", stdout)
        self.assertEqual("", stderr)
        self.assertNotIn(candidate, stdout + stderr)

    def test_invalid_evaluation_prints_only_contractual_failures_and_status_one(self) -> None:
        candidate = chr(0x61) * 11

        status, stdout, stderr = self._run(["check"], lambda prompt: candidate)

        self.assertEqual(1, status)
        self.assertEqual("", stderr)
        self.assertEqual(
            "Contraseña no válida según la política v1.\n"
            "No cumple la longitud requerida.\n"
            "Falta una letra mayúscula.\n"
            "Falta un dígito decimal.\n"
            "Falta un carácter especial.\n",
            stdout,
        )
        self.assertNotIn(candidate, stdout + stderr)

    def test_whitespace_diagnostic_follows_main_rules_without_exposing_input(self) -> None:
        candidate = self._valid_candidate() + chr(0x2003)

        status, stdout, stderr = self._run(["check"], lambda prompt: candidate)

        self.assertEqual(1, status)
        self.assertEqual("", stderr)
        self.assertEqual(
            "Contraseña no válida según la política v1.\n"
            "No se permiten espacios en blanco.\n",
            stdout,
        )
        self.assertNotIn(candidate, stdout)

    def test_missing_help_or_extra_arguments_return_usage_without_reading(self) -> None:
        reader = Mock()
        for arguments in ([], ["--help"], ["check", "extra"], ["unknown"]):
            with self.subTest(arguments=arguments):
                status, stdout, stderr = self._run(arguments, reader)
                self.assertEqual((2, "", USAGE), (status, stdout, stderr))
        reader.assert_not_called()

    def test_cancelled_or_unavailable_secure_input_returns_safe_error(self) -> None:
        secret = self._valid_candidate()
        failures = (
            EOFError(secret),
            KeyboardInterrupt(),
            OSError(secret),
            UnicodeError(secret),
        )
        for failure in failures:
            with self.subTest(failure=type(failure).__name__):
                status, stdout, stderr = self._run(
                    ["check"], self._raising_reader(failure)
                )
                self.assertEqual((1, "", f"{SECURE_INPUT_ERROR}\n"), (status, stdout, stderr))
                self.assertNotIn(secret, stdout + stderr)
                self.assertNotIn("Traceback", stdout + stderr)

    def test_getpass_warning_is_treated_as_secure_input_failure(self) -> None:
        import getpass

        def warning_reader(prompt: str) -> str:
            warnings_message = "unsafe terminal"
            import warnings

            warnings.warn(warnings_message, getpass.GetPassWarning)
            return self._valid_candidate()

        status, stdout, stderr = self._run(["check"], warning_reader)

        self.assertEqual((1, "", f"{SECURE_INPUT_ERROR}\n"), (status, stdout, stderr))

    def test_unexpected_core_exception_is_replaced_by_safe_error(self) -> None:
        secret = self._valid_candidate()
        with patch("main.validate_password", side_effect=RuntimeError(secret)):
            status, stdout, stderr = self._run(["check"], lambda prompt: secret)

        self.assertEqual((1, "", f"{UNEXPECTED_ERROR}\n"), (status, stdout, stderr))
        self.assertNotIn(secret, stdout + stderr)
        self.assertNotIn("Traceback", stdout + stderr)

    def test_reader_receives_the_static_prompt_only(self) -> None:
        reader = Mock(return_value=self._valid_candidate())

        status, _, _ = self._run(["check"], reader)

        self.assertEqual(0, status)
        reader.assert_called_once_with(PROMPT)

    @staticmethod
    def _raising_reader(failure: BaseException):
        def reader(prompt: str) -> str:
            raise failure

        return reader

    @staticmethod
    def _valid_candidate() -> str:
        return chr(0x41) + chr(0x61) + chr(0x31) + chr(0x21) + (chr(0x78) * 8)

    @staticmethod
    def _run(arguments: list[str], reader: object) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        status = run(arguments, stdout=stdout, stderr=stderr, password_reader=reader)
        return status, stdout.getvalue(), stderr.getvalue()


if __name__ == "__main__":
    unittest.main()
