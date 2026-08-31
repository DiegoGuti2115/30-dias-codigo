"""Command-line interface for the Day 3 local JSON and CSV converter."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TextIO

from converters import (
    load_csv_records,
    load_json_records,
    write_csv_to_json,
    write_json_to_csv,
)
from validators import ConversionError, validate_input_file, validate_output_file


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser shared by runtime use and tests."""
    parser = argparse.ArgumentParser(
        description="Convierte archivos locales JSON y CSV sin inferir tipos desde CSV."
    )
    subcommands = parser.add_subparsers(dest="command", required=True, title="operaciones")

    for name, source_suffix, destination_suffix, help_text in (
        ("json-to-csv", ".json", ".csv", "Convierte una lista JSON de objetos planos a CSV."),
        ("csv-to-json", ".csv", ".json", "Convierte un CSV con cabeceras a una lista JSON."),
    ):
        command = subcommands.add_parser(name, help=help_text, description=help_text)
        command.add_argument("input", type=Path, help=f"Archivo de entrada {source_suffix}.")
        command.add_argument("output", type=Path, help=f"Archivo de salida {destination_suffix}.")
        command.add_argument(
            "--overwrite",
            action="store_true",
            help="Permite reemplazar un archivo de salida ya existente.",
        )
    return parser


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments without performing I/O."""
    return build_parser().parse_args(argv)


def run(arguments: argparse.Namespace, output: TextIO) -> int:
    """Execute a selected conversion and print its concise result."""
    if arguments.command == "json-to-csv":
        input_path = validate_input_file(arguments.input, ".json")
        output_path = validate_output_file(arguments.output, ".csv", arguments.overwrite)
        records = load_json_records(input_path)
        count = write_json_to_csv(records, output_path)
        print(f"Conversión completada: {count} registro(s) JSON a CSV en {output_path}", file=output)
        return 0

    if arguments.command == "csv-to-json":
        input_path = validate_input_file(arguments.input, ".csv")
        output_path = validate_output_file(arguments.output, ".json", arguments.overwrite)
        _headers, records = load_csv_records(input_path)
        count = write_csv_to_json(records, output_path)
        print(f"Conversión completada: {count} fila(s) CSV a JSON en {output_path}", file=output)
        return 0

    raise ConversionError(f"Operación no admitida: {arguments.command}")


def main(argv: Sequence[str] | None = None, output: TextIO | None = None) -> int:
    """Run the CLI and return a shell-friendly exit status."""
    stream = output or sys.stdout
    try:
        return run(parse_arguments(argv), stream)
    except ConversionError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
