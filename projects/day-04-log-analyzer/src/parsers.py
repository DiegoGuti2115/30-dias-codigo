"""Sequential parsers for the `common` and JSON Lines log formats."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping
from datetime import datetime
import json
from pathlib import Path
import re
from typing import Any, Literal

from models import (
    DiagnosticCode,
    InputReadError,
    LineDiagnostic,
    LineResult,
    LogEvent,
    ParseBatch,
    SUPPORTED_LEVELS,
)

LogFormat = Literal["common", "jsonl"]
LineParser = Callable[[str, int], LineResult]

_COMMON_PATTERN = re.compile(r"^(\S+)[ \t]+(\S+)[ \t]+(.+)$")
_REQUIRED_JSON_FIELDS = ("timestamp", "level", "message")


def normalize_level(value: str) -> str | None:
    """Return an accepted uppercase severity level, or ``None`` when invalid."""

    normalized = value.upper()
    return normalized if normalized in SUPPORTED_LEVELS else None


def is_iso8601_timestamp(value: str) -> bool:
    """Validate the ISO 8601 timestamp syntax admitted by contract v1."""

    if not value or value != value.strip() or "T" not in value:
        return False

    normalized = f"{value[:-1]}+00:00" if value.endswith("Z") else value
    try:
        datetime.fromisoformat(normalized)
    except ValueError:
        return False
    return True


def _diagnostic(
    line_number: int,
    code: DiagnosticCode,
    message: str,
    detail: str | None = None,
) -> LineResult:
    return LineResult(
        line_number=line_number,
        diagnostic=LineDiagnostic(
            line_number=line_number,
            code=code,
            message=message,
            detail=detail,
        ),
    )


def _event(
    line_number: int,
    timestamp: str,
    level: str,
    message: str,
    metadata: Mapping[str, Any] | None = None,
) -> LineResult:
    return LineResult(
        line_number=line_number,
        event=LogEvent(
            line_number=line_number,
            timestamp=timestamp,
            level=level,
            message=message,
            metadata={} if metadata is None else metadata,
        ),
    )


def parse_common_line(line: str, line_number: int) -> LineResult:
    """Parse one physical line using ``<TIMESTAMP> <LEVEL> <MESSAGE>``."""

    content = line.rstrip("\r\n")
    if not content.strip():
        return _diagnostic(
            line_number,
            DiagnosticCode.BLANK_LINE,
            "La línea está vacía o contiene solo espacios.",
        )

    match = _COMMON_PATTERN.fullmatch(content)
    if match is None:
        return _diagnostic(
            line_number,
            DiagnosticCode.COMMON_STRUCTURE,
            "La línea common debe contener timestamp, nivel y mensaje.",
        )

    timestamp, raw_level, message = match.groups()
    if not is_iso8601_timestamp(timestamp):
        return _diagnostic(
            line_number,
            DiagnosticCode.INVALID_TIMESTAMP,
            "El timestamp no tiene sintaxis ISO 8601 válida.",
        )

    level = normalize_level(raw_level)
    if level is None:
        return _diagnostic(
            line_number,
            DiagnosticCode.INVALID_LEVEL,
            "El nivel de severidad no está admitido.",
            detail=raw_level,
        )

    if not message.strip():
        return _diagnostic(
            line_number,
            DiagnosticCode.EMPTY_FIELD,
            "El mensaje no puede estar vacío.",
            detail="message",
        )

    return _event(line_number, timestamp, level, message)


def parse_jsonl_line(line: str, line_number: int) -> LineResult:
    """Parse one physical line containing an independent JSON object."""

    content = line.rstrip("\r\n")
    if not content.strip():
        return _diagnostic(
            line_number,
            DiagnosticCode.BLANK_LINE,
            "La línea está vacía o contiene solo espacios.",
        )

    try:
        payload = json.loads(content)
    except json.JSONDecodeError as error:
        return _diagnostic(
            line_number,
            DiagnosticCode.INVALID_JSON,
            "La línea no contiene JSON válido.",
            detail=f"posición {error.pos}",
        )

    if not isinstance(payload, dict):
        return _diagnostic(
            line_number,
            DiagnosticCode.JSON_NOT_OBJECT,
            "La línea JSON Lines debe contener un objeto JSON.",
        )

    for field_name in _REQUIRED_JSON_FIELDS:
        if field_name not in payload:
            return _diagnostic(
                line_number,
                DiagnosticCode.MISSING_FIELD,
                "Falta un campo obligatorio.",
                detail=field_name,
            )
        if not isinstance(payload[field_name], str):
            return _diagnostic(
                line_number,
                DiagnosticCode.INVALID_FIELD_TYPE,
                "Un campo obligatorio debe ser una cadena.",
                detail=field_name,
            )
        if not payload[field_name].strip():
            return _diagnostic(
                line_number,
                DiagnosticCode.EMPTY_FIELD,
                "Un campo obligatorio no puede estar vacío.",
                detail=field_name,
            )

    timestamp = payload["timestamp"]
    raw_level = payload["level"]
    message = payload["message"]

    if not is_iso8601_timestamp(timestamp):
        return _diagnostic(
            line_number,
            DiagnosticCode.INVALID_TIMESTAMP,
            "El timestamp no tiene sintaxis ISO 8601 válida.",
        )

    level = normalize_level(raw_level)
    if level is None:
        return _diagnostic(
            line_number,
            DiagnosticCode.INVALID_LEVEL,
            "El nivel de severidad no está admitido.",
            detail=raw_level,
        )

    metadata = {
        key: value
        for key, value in payload.items()
        if key not in _REQUIRED_JSON_FIELDS
    }
    return _event(line_number, timestamp, level, message, metadata)


def get_line_parser(log_format: LogFormat) -> LineParser:
    """Return the parser selected explicitly by the v1 format contract."""

    if log_format == "common":
        return parse_common_line
    if log_format == "jsonl":
        return parse_jsonl_line
    raise ValueError(f"Formato de log no admitido: {log_format}")


def iter_parse_lines(lines: Iterable[str], log_format: LogFormat) -> Iterator[LineResult]:
    """Consume an iterable once and yield one ordered outcome for every line."""

    parser = get_line_parser(log_format)
    for line_number, line in enumerate(lines, start=1):
        yield parser(line, line_number)


def parse_lines(lines: Iterable[str], log_format: LogFormat) -> ParseBatch:
    """Return the ordered parser outcomes for a text-line iterable."""

    return ParseBatch(tuple(iter_parse_lines(lines, log_format)))


def parse_file(path: Path, log_format: LogFormat) -> ParseBatch:
    """Read a UTF-8 file sequentially and parse it using the selected format.

    Decode and operating-system errors are wrapped so the later CLI phase can map
    them to the contract's input-error exit status without exposing a traceback.
    """

    try:
        with path.open("r", encoding="utf-8", newline=None) as source:
            return parse_lines(source, log_format)
    except (OSError, UnicodeDecodeError) as error:
        raise InputReadError(f"No se pudo leer el archivo de log: {path}") from error
