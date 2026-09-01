"""Domain models shared by the sequential log parsers."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, TypeAlias


SUPPORTED_LEVELS: tuple[str, ...] = (
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
)
"""Severity levels admitted by contract v1, in ascending severity order."""

Metadata: TypeAlias = Mapping[str, Any]


class DiagnosticCode(str, Enum):
    """Stable categories for an input line that cannot be normalized."""

    BLANK_LINE = "blank_line"
    COMMON_STRUCTURE = "common_structure"
    INVALID_TIMESTAMP = "invalid_timestamp"
    INVALID_LEVEL = "invalid_level"
    INVALID_JSON = "invalid_json"
    JSON_NOT_OBJECT = "json_not_object"
    MISSING_FIELD = "missing_field"
    INVALID_FIELD_TYPE = "invalid_field_type"
    EMPTY_FIELD = "empty_field"


@dataclass(frozen=True, slots=True)
class LogEvent:
    """A valid log event normalized independently of its source format."""

    line_number: int
    timestamp: str
    level: str
    message: str
    metadata: Metadata = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.line_number < 1:
            raise ValueError("line_number must be positive")
        if self.level not in SUPPORTED_LEVELS:
            raise ValueError("level must be one of the supported severity levels")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True, slots=True)
class LineDiagnostic:
    """A deterministic explanation for one rejected physical input line."""

    line_number: int
    code: DiagnosticCode
    message: str
    detail: str | None = None

    def __post_init__(self) -> None:
        if self.line_number < 1:
            raise ValueError("line_number must be positive")


@dataclass(frozen=True, slots=True)
class LineResult:
    """The mutually exclusive outcome of parsing a single physical line."""

    line_number: int
    event: LogEvent | None = None
    diagnostic: LineDiagnostic | None = None

    def __post_init__(self) -> None:
        if self.line_number < 1:
            raise ValueError("line_number must be positive")
        if (self.event is None) == (self.diagnostic is None):
            raise ValueError("a line result must contain exactly one outcome")
        if self.event is not None and self.event.line_number != self.line_number:
            raise ValueError("event line number must match the result")
        if self.diagnostic is not None and self.diagnostic.line_number != self.line_number:
            raise ValueError("diagnostic line number must match the result")


@dataclass(frozen=True, slots=True)
class ParseBatch:
    """Ordered results emitted while consuming an iterable of lines once."""

    results: tuple[LineResult, ...]

    @property
    def events(self) -> tuple[LogEvent, ...]:
        return tuple(result.event for result in self.results if result.event is not None)

    @property
    def diagnostics(self) -> tuple[LineDiagnostic, ...]:
        return tuple(
            result.diagnostic
            for result in self.results
            if result.diagnostic is not None
        )


class InputReadError(RuntimeError):
    """Raised when a text file cannot be read as a UTF-8 log input."""
