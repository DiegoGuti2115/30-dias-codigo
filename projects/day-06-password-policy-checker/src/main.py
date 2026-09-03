"""Command-line interface for the local password-policy checker v1."""

from __future__ import annotations

import getpass
import sys
import warnings
from collections.abc import Callable, Sequence
from typing import Final, TextIO

from reporters import format_validation_result
from validator import validate_password


USAGE: Final = "Uso: python src/main.py check\n"
SECURE_INPUT_ERROR: Final = "No se pudo solicitar una contraseña de forma segura."
UNEXPECTED_ERROR: Final = "No se pudo completar la comprobación de forma segura."
PROMPT: Final = "Contraseña: "

PasswordReader = Callable[[str], str]


def run(
    arguments: Sequence[str] | None = None,
    *,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
    password_reader: PasswordReader = getpass.getpass,
) -> int:
    """Run the v1 CLI and return a documented, secret-safe exit status."""
    supplied_arguments = list(sys.argv[1:] if arguments is None else arguments)
    output = sys.stdout if stdout is None else stdout
    errors = sys.stderr if stderr is None else stderr

    if supplied_arguments != ["check"]:
        errors.write(USAGE)
        return 2

    password: str | None = None
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", getpass.GetPassWarning)
            password = password_reader(PROMPT)
    except (EOFError, KeyboardInterrupt, getpass.GetPassWarning, OSError, UnicodeError):
        errors.write(f"{SECURE_INPUT_ERROR}\n")
        return 1
    except Exception:
        errors.write(f"{SECURE_INPUT_ERROR}\n")
        return 1

    try:
        result = validate_password(password)
        output.write(format_validation_result(result))
        return 0 if result.is_valid else 1
    except Exception:
        errors.write(f"{UNEXPECTED_ERROR}\n")
        return 1
    finally:
        if password is not None:
            del password


if __name__ == "__main__":
    raise SystemExit(run())
