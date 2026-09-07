"""Route validation and non-destructive publication for the Day 08 CLI."""

from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cleaner import CleaningResult


class PathValidationError(ValueError):
    """Raised when requested input or output routes violate the v1 contract."""


class PublicationError(RuntimeError):
    """Raised when owned temporary or final output artifacts cannot be published."""


@dataclass(frozen=True)
class ExecutionPaths:
    """Normalized, validated paths for one CLI invocation."""

    source: Path
    plan: Path
    output_csv: Path
    summary_json: Path


def validate_execution_paths(
    source: str | Path,
    plan: str | Path,
    output_csv: str | Path,
    summary_json: str | Path,
) -> ExecutionPaths:
    """Validate all four routes before the core loads or transforms input."""

    source_path = _validate_input_path(source, "source")
    plan_path = _validate_input_path(plan, "plan")
    csv_path = _validate_output_path(output_csv)
    summary_path = _validate_output_path(summary_json)

    locations = (source_path, plan_path, csv_path, summary_path)
    if len(set(locations)) != len(locations) or csv_path.name == summary_path.name:
        raise PathValidationError("output_path_conflict")

    _probe_writable_parent(csv_path.parent)
    _probe_writable_parent(summary_path.parent)
    return ExecutionPaths(source_path, plan_path, csv_path, summary_path)


def publish_result(result: "CleaningResult", paths: ExecutionPaths) -> None:
    """Write both artifacts to owned temporaries, then publish both or clean up."""

    csv_temp: Path | None = None
    summary_temp: Path | None = None
    published: list[Path] = []
    try:
        csv_temp = _create_temp_path(paths.output_csv.parent, ".csv-cleaner-", ".csv.tmp")
        summary_temp = _create_temp_path(paths.summary_json.parent, ".csv-cleaner-", ".json.tmp")
        _write_csv(csv_temp, result.headers, result.rows)
        _write_summary(summary_temp, result.summary())

        _ensure_output_still_available(paths.output_csv)
        _ensure_output_still_available(paths.summary_json)
        os.replace(csv_temp, paths.output_csv)
        published.append(paths.output_csv)
        csv_temp = None
        os.replace(summary_temp, paths.summary_json)
        published.append(paths.summary_json)
        summary_temp = None
    except (OSError, TypeError, ValueError) as error:
        for published_path in reversed(published):
            _remove_owned_file(published_path)
        raise PublicationError("publication_failed") from error
    finally:
        if csv_temp is not None:
            _remove_owned_file(csv_temp)
        if summary_temp is not None:
            _remove_owned_file(summary_temp)


def _validate_input_path(value: str | Path, label: str) -> Path:
    path = Path(value)
    try:
        resolved = path.resolve(strict=True)
    except OSError as error:
        raise PathValidationError(f"{label}_path_invalid") from error
    if not resolved.is_file():
        raise PathValidationError(f"{label}_path_invalid")
    try:
        with resolved.open("rb"):
            pass
    except OSError as error:
        raise PathValidationError(f"{label}_path_unreadable") from error
    return resolved


def _validate_output_path(value: str | Path) -> Path:
    supplied = Path(value)
    if os.path.lexists(supplied):
        raise PathValidationError("output_path_conflict")
    try:
        parent = supplied.parent.resolve(strict=True)
    except OSError as error:
        raise PathValidationError("output_parent_invalid") from error
    if not parent.is_dir():
        raise PathValidationError("output_parent_invalid")
    return parent / supplied.name


def _probe_writable_parent(parent: Path) -> None:
    try:
        with NamedTemporaryFile(mode="wb", prefix=".csv-cleaner-probe-", dir=parent, delete=True):
            pass
    except OSError as error:
        raise PathValidationError("output_parent_unwritable") from error


def _create_temp_path(parent: Path, prefix: str, suffix: str) -> Path:
    with NamedTemporaryFile(mode="wb", prefix=prefix, suffix=suffix, dir=parent, delete=False) as handle:
        return Path(handle.name)


def _ensure_output_still_available(path: Path) -> None:
    if os.path.lexists(path):
        raise PublicationError("output_path_conflict")


def _write_csv(path: Path, headers: tuple[str, ...], rows: tuple[tuple[str, ...], ...]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter=",", quotechar='"', lineterminator="\n")
        writer.writerow(headers)
        writer.writerows(rows)


def _write_summary(path: Path, summary: dict[str, object]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def _remove_owned_file(path: Path) -> None:
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass
