"""Pure aggregation and severity filtering for normalized log events."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Literal

from models import LogEvent, ParseBatch, SUPPORTED_LEVELS

LogFormat = Literal["common", "jsonl"]
ERROR_THRESHOLD = "ERROR"
"""Lowest normalized level included in the v1 error report."""

_LEVEL_RANK = {level: rank for rank, level in enumerate(SUPPORTED_LEVELS)}
_ERROR_THRESHOLD_RANK = _LEVEL_RANK[ERROR_THRESHOLD]


@dataclass(frozen=True, slots=True)
class MessageFrequency:
    """A message and its deterministic frequency within a parsed batch."""

    message: str
    count: int

    def __post_init__(self) -> None:
        if not self.message:
            raise ValueError("message must not be empty")
        if self.count < 1:
            raise ValueError("count must be positive")


@dataclass(frozen=True, slots=True)
class AnalysisResult:
    """Metrics and selected error events derived from one parsed input."""

    log_format: LogFormat
    total_lines: int
    valid_events: int
    invalid_lines: int
    level_counts: tuple[tuple[str, int], ...]
    top_messages: tuple[MessageFrequency, ...]
    error_events: tuple[LogEvent, ...]

    def __post_init__(self) -> None:
        if self.total_lines < 0 or self.valid_events < 0 or self.invalid_lines < 0:
            raise ValueError("analysis counts must not be negative")
        if self.total_lines != self.valid_events + self.invalid_lines:
            raise ValueError("total lines must equal valid events plus invalid lines")
        if tuple(level for level, _ in self.level_counts) != SUPPORTED_LEVELS:
            raise ValueError("level counts must use all supported levels in severity order")
        if any(count < 0 for _, count in self.level_counts):
            raise ValueError("level counts must not be negative")
        if sum(count for _, count in self.level_counts) != self.valid_events:
            raise ValueError("level counts must total valid events")
        if any(event.level not in ("ERROR", "CRITICAL") for event in self.error_events):
            raise ValueError("error events must meet the fixed error threshold")

    @property
    def error_line_numbers(self) -> tuple[int, ...]:
        """Return selected event line numbers in their physical input order."""

        return tuple(event.line_number for event in self.error_events)

    @property
    def level_count_map(self) -> dict[str, int]:
        """Return a copy of counts keyed by the stable severity order."""

        return dict(self.level_counts)


def is_error_level(level: str) -> bool:
    """Return whether a normalized level meets the v1 fixed error threshold."""

    try:
        return _LEVEL_RANK[level] >= _ERROR_THRESHOLD_RANK
    except KeyError as error:
        raise ValueError(f"Nivel de severidad no admitido: {level}") from error


def filter_error_events(events: tuple[LogEvent, ...]) -> tuple[LogEvent, ...]:
    """Select ERROR and CRITICAL events without changing their input order."""

    return tuple(event for event in events if is_error_level(event.level))


def analyze_batch(batch: ParseBatch, log_format: LogFormat, *, top_limit: int = 3) -> AnalysisResult:
    """Compute deterministic v1 metrics from ordered parser outcomes.

    The parser owns normalization and diagnostics. This function only aggregates
    accepted events and preserves their physical order in the error selection.
    """

    if log_format not in ("common", "jsonl"):
        raise ValueError(f"Formato de log no admitido: {log_format}")
    if top_limit < 0:
        raise ValueError("top_limit must not be negative")

    events = batch.events
    level_counts = Counter(event.level for event in events)
    message_counts = Counter(event.message for event in events)
    first_appearance: dict[str, int] = {}
    for event in events:
        first_appearance.setdefault(event.message, event.line_number)

    ordered_messages = sorted(
        message_counts,
        key=lambda message: (-message_counts[message], first_appearance[message]),
    )
    top_messages = tuple(
        MessageFrequency(message=message, count=message_counts[message])
        for message in ordered_messages[:top_limit]
    )

    return AnalysisResult(
        log_format=log_format,
        total_lines=len(batch.results),
        valid_events=len(events),
        invalid_lines=len(batch.diagnostics),
        level_counts=tuple((level, level_counts[level]) for level in SUPPORTED_LEVELS),
        top_messages=top_messages,
        error_events=filter_error_events(events),
    )
