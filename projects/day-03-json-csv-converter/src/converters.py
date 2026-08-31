"""File conversion services for the local JSON to CSV command-line tool."""

from __future__ import annotations

import csv
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from validators import ConversionError, validate_headers, validate_json_records


def collect_headers(records: list[dict[str, Any]]) -> list[str]:
    """Collect record keys in first-seen order for deterministic CSV columns."""
    headers: list[str] = []
    seen: set[str] = set()
    for record in records:
        for key in record:
            if key not in seen:
                seen.add(key)
                headers.append(key)
    return headers


def json_value_to_cell(value: Any) -> str:
    """Render a permitted JSON scalar as a stable CSV cell."""
    if value is None:
        return ""
    if value is True:
        return "true"
    if value is False:
        return "false"
    return str(value)


def load_json_records(input_path: Path) -> list[dict[str, Any]]:
    """Load a UTF-8 JSON file and validate the supported JSON shape."""
    try:
        with input_path.open("r", encoding="utf-8-sig") as source:
            payload = json.load(source)
    except json.JSONDecodeError as error:
        raise ConversionError(
            f"El JSON no es válido en la línea {error.lineno}, columna {error.colno}: {error.msg}"
        ) from error
    except (OSError, UnicodeDecodeError) as error:
        raise ConversionError(f"No se pudo leer el JSON: {error}") from error
    return validate_json_records(payload)


def load_csv_records(input_path: Path) -> tuple[list[str], list[dict[str, str]]]:
    """Load CSV headers and rows, preserving every field as text."""
    try:
        with input_path.open("r", encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source, restkey="__extra_columns__", restval="")
            headers = validate_headers(reader.fieldnames)
            records: list[dict[str, str]] = []
            for row_number, row in enumerate(reader, start=2):
                extra = row.pop("__extra_columns__", None)
                if extra is not None:
                    raise ConversionError(
                        f"La fila CSV {row_number} contiene más valores que cabeceras."
                    )
                records.append({header: row[header] if row[header] is not None else "" for header in headers})
    except (OSError, UnicodeDecodeError, csv.Error) as error:
        raise ConversionError(f"No se pudo leer el CSV: {error}") from error
    return headers, records


def write_json_to_csv(records: list[dict[str, Any]], output_path: Path) -> int:
    """Write validated JSON records to CSV atomically and return their count."""
    headers = collect_headers(records)
    _write_atomically(output_path, lambda target: _write_csv(target, headers, records))
    return len(records)


def write_csv_to_json(records: list[dict[str, str]], output_path: Path) -> int:
    """Write CSV records as a formatted JSON array atomically and return their count."""
    _write_atomically(output_path, lambda target: _write_json(target, records))
    return len(records)


def _write_csv(target: Path, headers: list[str], records: list[dict[str, Any]]) -> None:
    with target.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=headers, extrasaction="raise")
        writer.writeheader()
        for record in records:
            writer.writerow({header: json_value_to_cell(record.get(header)) for header in headers})


def _write_json(target: Path, records: list[dict[str, str]]) -> None:
    with target.open("w", encoding="utf-8", newline="\n") as destination:
        json.dump(records, destination, ensure_ascii=False, indent=2)
        destination.write("\n")


def _write_atomically(output_path: Path, writer: Any) -> None:
    """Write through a sibling temporary file so failed conversions leave no output."""
    descriptor = -1
    temporary_path: Path | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{output_path.name}.", suffix=".tmp", dir=output_path.parent
        )
        os.close(descriptor)
        descriptor = -1
        temporary_path = Path(temporary_name)
        writer(temporary_path)
        temporary_path.replace(output_path)
    except (OSError, csv.Error, TypeError, ValueError) as error:
        raise ConversionError(f"No se pudo escribir la salida: {error}") from error
    finally:
        if descriptor != -1:
            os.close(descriptor)
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
