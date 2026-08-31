"""Validation rules for the supported JSON and CSV shapes."""

from __future__ import annotations

import math
from collections.abc import Sequence
from pathlib import Path
from typing import Any


class ConversionError(Exception):
    """Raised when an input or output cannot be safely converted."""


def validate_input_file(path: Path, expected_suffix: str) -> Path:
    """Return a validated input path with the expected file extension."""
    candidate = path.expanduser()
    if candidate.suffix.casefold() != expected_suffix:
        raise ConversionError(
            f"La entrada debe usar la extensión {expected_suffix}: {candidate}"
        )
    if not candidate.is_file():
        raise ConversionError(f"El archivo de entrada no existe o no es legible: {candidate}")
    return candidate


def validate_output_file(path: Path, expected_suffix: str, overwrite: bool) -> Path:
    """Return a safe output path, rejecting accidental overwrites."""
    candidate = path.expanduser()
    if candidate.suffix.casefold() != expected_suffix:
        raise ConversionError(
            f"La salida debe usar la extensión {expected_suffix}: {candidate}"
        )
    if not candidate.parent.is_dir():
        raise ConversionError(f"El directorio de salida no existe: {candidate.parent}")
    if candidate.exists() and not overwrite:
        raise ConversionError(
            f"El archivo de salida ya existe y no se sobrescribirá: {candidate}. "
            "Use --overwrite para confirmarlo."
        )
    if candidate.exists() and not candidate.is_file():
        raise ConversionError(f"La ruta de salida no es un archivo: {candidate}")
    return candidate


def validate_json_records(payload: Any) -> list[dict[str, Any]]:
    """Validate a JSON root as a list of flat objects with scalar values."""
    if not isinstance(payload, list):
        raise ConversionError("El JSON debe tener una lista de objetos como raíz.")
    if not payload:
        raise ConversionError("El JSON no puede estar vacío: se requiere al menos un registro.")

    records: list[dict[str, Any]] = []
    allowed_scalar_types = (str, int, float, bool, type(None))
    for index, record in enumerate(payload, start=1):
        if not isinstance(record, dict):
            raise ConversionError(f"El registro JSON {index} debe ser un objeto.")
        if not record:
            raise ConversionError(f"El registro JSON {index} no puede estar vacío.")
        normalized: dict[str, Any] = {}
        for key, value in record.items():
            if not isinstance(key, str) or not key:
                raise ConversionError(
                    f"El registro JSON {index} contiene una clave vacía o no textual."
                )
            if isinstance(value, (dict, list)):
                raise ConversionError(
                    f"El registro JSON {index}, clave {key!r}, contiene una estructura "
                    "anidada no admitida."
                )
            if not isinstance(value, allowed_scalar_types):
                raise ConversionError(
                    f"El registro JSON {index}, clave {key!r}, contiene un valor no admitido."
                )
            if isinstance(value, float) and not math.isfinite(value):
                raise ConversionError(
                    f"El registro JSON {index}, clave {key!r}, contiene un número no finito."
                )
            normalized[key] = value
        records.append(normalized)
    return records


def validate_headers(headers: Sequence[str] | None) -> list[str]:
    """Validate CSV headers and return a concrete list."""
    if headers is None:
        raise ConversionError("El CSV está vacío o no contiene cabeceras.")
    normalized = list(headers)
    if not normalized:
        raise ConversionError("El CSV está vacío o no contiene cabeceras.")
    if any(not header or not header.strip() for header in normalized):
        raise ConversionError("Las cabeceras CSV no pueden estar vacías.")
    duplicates = {header for header in normalized if normalized.count(header) > 1}
    if duplicates:
        names = ", ".join(sorted(repr(header) for header in duplicates))
        raise ConversionError(f"Las cabeceras CSV están duplicadas: {names}")
    return normalized
