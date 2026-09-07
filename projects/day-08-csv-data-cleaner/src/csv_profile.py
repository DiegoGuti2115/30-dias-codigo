"""Contractual CSV loading and structural profiling for Day 08."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

MAX_SOURCE_BYTES = 10 * 1024 * 1024
MAX_DATA_ROWS = 10_000
MAX_COLUMNS = 100
FORMULA_PREFIXES = ("=", "+", "-", "@")


class CsvContractError(ValueError):
    """Raised when a CSV does not satisfy the v1 input contract."""


@dataclass(frozen=True)
class CsvDataset:
    """A validated in-memory CSV, preserving its decoded text values."""

    source_name: str
    size_bytes: int
    headers: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]

    @property
    def column_count(self) -> int:
        return len(self.headers)

    @property
    def data_row_count(self) -> int:
        return len(self.rows)


@dataclass(frozen=True)
class StructuralProfile:
    """The aggregate-only metrics permitted by the v1 summary contract."""

    headers: tuple[str, ...]
    empty_value_count: int
    empty_row_count: int
    exact_duplicate_row_count: int
    formula_like_cell_count: int

    def as_dict(self) -> dict[str, object]:
        return {
            "headers": list(self.headers),
            "empty_value_count": self.empty_value_count,
            "empty_row_count": self.empty_row_count,
            "exact_duplicate_row_count": self.exact_duplicate_row_count,
            "formula_like_cell_count": self.formula_like_cell_count,
        }


def load_csv(source: str | Path) -> CsvDataset:
    """Read one contract-compliant comma-delimited UTF-8 CSV into memory.

    The reader deliberately does not inspect field contents to infer another
    dialect. A semicolon in a field remains ordinary text under the v1 comma
    dialect.
    """

    source_path = Path(source)
    try:
        size_bytes = source_path.stat().st_size
    except OSError as error:
        raise CsvContractError("csv_source_unavailable") from error

    if size_bytes > MAX_SOURCE_BYTES:
        raise CsvContractError("csv_size_limit")

    previous_field_limit = csv.field_size_limit()
    csv.field_size_limit(MAX_SOURCE_BYTES)
    try:
        with source_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(
                handle,
                delimiter=",",
                quotechar='"',
                doublequote=True,
                escapechar=None,
                skipinitialspace=False,
                strict=True,
            )
            try:
                headers = next(reader)
            except StopIteration as error:
                raise CsvContractError("csv_missing_header") from error

            _validate_headers(headers)
            rows: list[tuple[str, ...]] = []
            for row in reader:
                if len(row) != len(headers):
                    raise CsvContractError("csv_irregular_row")
                rows.append(tuple(row))
                if len(rows) > MAX_DATA_ROWS:
                    raise CsvContractError("csv_row_limit")
    except UnicodeDecodeError as error:
        raise CsvContractError("csv_invalid_encoding") from error
    except csv.Error as error:
        raise CsvContractError("csv_malformed") from error
    except OSError as error:
        raise CsvContractError("csv_source_unavailable") from error
    finally:
        csv.field_size_limit(previous_field_limit)

    return CsvDataset(
        source_name=source_path.name,
        size_bytes=size_bytes,
        headers=tuple(headers),
        rows=tuple(rows),
    )


def validate_normalized_headers(headers: Sequence[str]) -> tuple[str, ...]:
    """Return trimmed headers or reject a normalization incompatibility."""

    normalized = tuple(header.strip() for header in headers)
    try:
        _validate_headers(normalized)
    except CsvContractError as error:
        raise CsvContractError("header_normalization_collision") from error
    return normalized


def profile_csv(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> StructuralProfile:
    """Calculate contract-approved structural metrics without exposing cells."""

    frozen_rows = tuple(tuple(row) for row in rows)
    seen: set[tuple[str, ...]] = set()
    duplicate_count = 0
    for row in frozen_rows:
        if row in seen:
            duplicate_count += 1
        else:
            seen.add(row)

    return StructuralProfile(
        headers=tuple(headers),
        empty_value_count=sum(cell == "" for row in frozen_rows for cell in row),
        empty_row_count=sum(all(cell == "" for cell in row) for row in frozen_rows),
        exact_duplicate_row_count=duplicate_count,
        formula_like_cell_count=sum(
            bool(cell) and cell.startswith(FORMULA_PREFIXES)
            for row in frozen_rows
            for cell in row
        ),
    )


def _validate_headers(headers: Sequence[str]) -> None:
    if not headers:
        raise CsvContractError("csv_missing_header")
    if len(headers) > MAX_COLUMNS:
        raise CsvContractError("csv_column_limit")
    if any(header == "" for header in headers) or len(set(headers)) != len(headers):
        raise CsvContractError("csv_invalid_headers")
