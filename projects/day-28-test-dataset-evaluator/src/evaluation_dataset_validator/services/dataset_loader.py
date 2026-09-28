"""Adaptadores locales de JSON, JSONL y CSV hacia registros de evaluación."""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from evaluation_dataset_validator.errors import (
    FileAccessError,
    InvalidDatasetError,
    InvalidJsonError,
)
from evaluation_dataset_validator.models.contracts import SourceLocation


SUPPORTED_INPUT_FORMATS = ("json", "jsonl", "csv")


@dataclass(frozen=True, slots=True)
class SourceRecord:
    """Payload normalizado junto con la posición de inicio de su origen."""

    payload: Any
    location: SourceLocation


def load_dataset(source: Path, input_format: str = "auto") -> list[SourceRecord]:
    """Load a dataset through the selected local adapter."""
    resolved_format = _resolve_input_format(source, input_format)
    raw_content = _read_source(source)
    if resolved_format == "json":
        return _load_json_dataset(source, raw_content)
    if resolved_format == "jsonl":
        return _load_jsonl_dataset(source, raw_content)
    return _load_csv_dataset(source, raw_content)


def load_json_dataset(source: Path) -> list[Any]:
    """Preserve the phase-one JSON-array loader public API."""
    return [record.payload for record in load_dataset(source, "json")]


def _resolve_input_format(source: Path, input_format: str) -> str:
    if input_format == "auto":
        suffix = source.suffix.lower()
        inferred_formats = {".json": "json", ".jsonl": "jsonl", ".ndjson": "jsonl", ".csv": "csv"}
        resolved_format = inferred_formats.get(suffix)
        if resolved_format is None:
            raise InvalidDatasetError(
                "No se puede detectar el formato de entrada; use --input-format json, jsonl o csv."
            )
        return resolved_format
    if input_format not in SUPPORTED_INPUT_FORMATS:
        raise InvalidDatasetError(f"Formato de entrada no admitido: {input_format}.")
    return input_format


def _read_source(source: Path) -> str:
    try:
        return source.read_text(encoding="utf-8")
    except OSError as error:
        raise FileAccessError(source) from error


def _load_json_dataset(source: Path, raw_content: str) -> list[SourceRecord]:
    try:
        payload = json.loads(raw_content)
    except json.JSONDecodeError as error:
        _raise_invalid_json(source, error)
    if not isinstance(payload, list):
        raise InvalidDatasetError("El dataset JSON debe ser un array de registros.")
    return [
        SourceRecord(item, SourceLocation(file=str(source), line=index + 1, column=1))
        for index, item in enumerate(payload)
    ]


def _load_jsonl_dataset(source: Path, raw_content: str) -> list[SourceRecord]:
    records: list[SourceRecord] = []
    for line_number, raw_line in enumerate(raw_content.splitlines(), start=1):
        if not raw_line.strip():
            continue
        try:
            payload = json.loads(raw_line)
        except json.JSONDecodeError as error:
            _raise_invalid_json(source, error, line_offset=line_number - 1)
        if not isinstance(payload, dict):
            raise InvalidDatasetError(f"La línea {line_number} de {source} debe ser un objeto JSON.")
        records.append(SourceRecord(payload, SourceLocation(file=str(source), line=line_number, column=1)))
    return records


def _load_csv_dataset(source: Path, raw_content: str) -> list[SourceRecord]:
    try:
        reader = csv.DictReader(io.StringIO(raw_content))
        if reader.fieldnames is None:
            raise InvalidDatasetError("El CSV debe incluir una fila de encabezados.")
        required_columns = {"id", "input", "expected_output"}
        missing_columns = required_columns.difference(reader.fieldnames)
        if missing_columns:
            raise InvalidDatasetError(
                f"El CSV no incluye las columnas requeridas: {', '.join(sorted(missing_columns))}."
            )
        records = []
        for line_number, row in enumerate(reader, start=2):
            records.append(
                SourceRecord(
                    _csv_row_to_record(row),
                    SourceLocation(file=str(source), line=line_number, column=1),
                )
            )
        return records
    except csv.Error as error:
        raise InvalidDatasetError(f"CSV inválido en {source}: {error}.") from error


def _csv_row_to_record(row: dict[str, str | None]) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    metadata_value = row.get("metadata")
    if metadata_value and metadata_value.strip():
        try:
            parsed_metadata = json.loads(metadata_value)
        except json.JSONDecodeError as error:
            raise InvalidDatasetError("La columna metadata del CSV debe contener un objeto JSON válido.") from error
        if not isinstance(parsed_metadata, dict):
            raise InvalidDatasetError("La columna metadata del CSV debe contener un objeto JSON.")
        metadata = parsed_metadata
    for column, value in row.items():
        if column.startswith("metadata.") and value not in (None, ""):
            metadata[column.removeprefix("metadata.")] = value
    return {
        "id": row.get("id"),
        "input": _decode_csv_value(row.get("input")),
        "expected_output": _decode_csv_value(row.get("expected_output")),
        "metadata": metadata,
    }


def _decode_csv_value(value: str | None) -> Any:
    if value is None:
        return None
    stripped = value.strip()
    if stripped.startswith(("{", "[")):
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            return value
    return value


def _raise_invalid_json(source: Path, error: json.JSONDecodeError, line_offset: int = 0) -> None:
    detail = f"{error.msg} (línea {error.lineno + line_offset}, columna {error.colno})"
    raise InvalidJsonError(source, detail) from error
