"""Command-line entry point for the v1 local log analyzer."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
import sys
from typing import NoReturn

from analyzer import analyze_batch
from models import InputReadError
from parsers import parse_file
from reporters import format_analysis

EXIT_SUCCESS = 0
EXIT_RUNTIME_ERROR = 1
EXIT_USAGE_ERROR = 2


def build_parser() -> argparse.ArgumentParser:
    """Create the v1 CLI parser without performing any file-system operation."""

    parser = argparse.ArgumentParser(
        prog="log-analyzer",
        description="Analiza un único archivo de logs common o JSON Lines en UTF-8.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)
    analyze = subcommands.add_parser(
        "analyze",
        help="normaliza un archivo y muestra su resumen agregado",
    )
    analyze.add_argument("log_path", type=Path, metavar="LOG_PATH", help="ruta a un archivo UTF-8")
    analyze.add_argument(
        "--format",
        dest="log_format",
        choices=("common", "jsonl"),
        required=True,
        help="formato de entrada seleccionado explícitamente",
    )
    analyze.add_argument(
        "--errors",
        action="store_true",
        help="añade los eventos ERROR y CRITICAL al resumen",
    )
    return parser


def _input_error(message: str) -> NoReturn:
    """Print one actionable input error without a traceback and exit consistently."""

    print(f"Error de entrada: {message}", file=sys.stderr)
    raise SystemExit(EXIT_RUNTIME_ERROR)


def run_analysis(log_path: Path, log_format: str, *, include_errors: bool) -> str:
    """Coordinate validated input, parsing, aggregation, and presentation."""

    try:
        if not log_path.exists():
            _input_error(f"la ruta no existe: {log_path}")
        if not log_path.is_file():
            _input_error(f"la ruta no es un archivo: {log_path}")
    except OSError:
        _input_error(f"no se pudo comprobar la ruta: {log_path}")

    try:
        batch = parse_file(log_path, log_format)  # type: ignore[arg-type]
    except InputReadError:
        _input_error(f"no se pudo leer como UTF-8: {log_path}")

    analysis = analyze_batch(batch, log_format)  # type: ignore[arg-type]
    if analysis.valid_events == 0:
        print(
            "Error de análisis: el archivo no contiene eventos válidos.",
            file=sys.stderr,
        )
        raise SystemExit(EXIT_RUNTIME_ERROR)

    return format_analysis(analysis, log_path, include_errors=include_errors)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the v1 CLI and return its documented process exit code."""

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    parser = build_parser()
    arguments = parser.parse_args(argv)

    try:
        output = run_analysis(
            arguments.log_path,
            arguments.log_format,
            include_errors=arguments.errors,
        )
    except SystemExit as error:
        return int(error.code)

    print(output)
    return EXIT_SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
