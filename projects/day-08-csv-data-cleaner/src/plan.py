"""Strict v1 cleaning-plan parsing and normalization."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

OPERATION_ORDER = (
    "normalize_headers",
    "drop_empty_rows",
    "trim_fields",
    "replace_missing_markers",
    "drop_exact_duplicates",
)
_PARAMETERLESS_OPERATIONS = frozenset(OPERATION_ORDER) - {"replace_missing_markers"}


class PlanValidationError(ValueError):
    """Raised when a JSON plan violates the closed v1 schema."""


@dataclass(frozen=True)
class CleaningOperation:
    """One validated operation, retaining only contract-approved parameters."""

    name: str
    markers: tuple[str, ...] = ()


@dataclass(frozen=True)
class CleaningPlan:
    """A validated plan whose operations are normalized to contractual order."""

    version: int
    operations: tuple[CleaningOperation, ...]

    @property
    def requested_operations(self) -> tuple[str, ...]:
        return tuple(operation.name for operation in self.operations)


def load_plan(path: str | Path) -> CleaningPlan:
    """Read a UTF-8-without-BOM JSON plan from a local regular file."""

    try:
        raw_bytes = Path(path).read_bytes()
    except OSError as error:
        raise PlanValidationError("plan_unavailable") from error
    if raw_bytes.startswith(b"\xef\xbb\xbf"):
        raise PlanValidationError("plan_invalid_encoding")
    try:
        document = json.loads(raw_bytes.decode("utf-8"))
    except UnicodeDecodeError as error:
        raise PlanValidationError("plan_invalid_encoding") from error
    except json.JSONDecodeError as error:
        raise PlanValidationError("plan_invalid_json") from error
    return parse_plan(document)


def parse_plan(document: Any) -> CleaningPlan:
    """Validate a decoded JSON value and produce its ordered internal model."""

    if not isinstance(document, dict):
        raise PlanValidationError("plan_root_not_object")
    if set(document) != {"version", "operations"}:
        raise PlanValidationError("plan_extra_root_key")
    if type(document["version"]) is not int or document["version"] != 1:
        raise PlanValidationError("plan_unsupported_version")

    raw_operations = document["operations"]
    if not isinstance(raw_operations, list) or not raw_operations or len(raw_operations) > len(OPERATION_ORDER):
        raise PlanValidationError("plan_invalid_operations")

    parsed: dict[str, CleaningOperation] = {}
    for raw_operation in raw_operations:
        operation = _parse_operation(raw_operation)
        if operation.name in parsed:
            raise PlanValidationError("plan_duplicate_operation")
        parsed[operation.name] = operation

    return CleaningPlan(
        version=1,
        operations=tuple(parsed[name] for name in OPERATION_ORDER if name in parsed),
    )


def _parse_operation(raw_operation: Any) -> CleaningOperation:
    if not isinstance(raw_operation, dict) or "operation" not in raw_operation:
        raise PlanValidationError("plan_invalid_operation")
    name = raw_operation["operation"]
    if not isinstance(name, str) or name not in OPERATION_ORDER:
        raise PlanValidationError("plan_unknown_operation")

    if name in _PARAMETERLESS_OPERATIONS:
        if set(raw_operation) != {"operation"}:
            raise PlanValidationError("plan_invalid_operation_keys")
        return CleaningOperation(name=name)

    if set(raw_operation) != {"operation", "markers"}:
        raise PlanValidationError("plan_invalid_markers")
    markers = raw_operation["markers"]
    if (
        not isinstance(markers, list)
        or not 1 <= len(markers) <= 10
        or any(not isinstance(marker, str) or marker == "" for marker in markers)
        or len(set(markers)) != len(markers)
    ):
        raise PlanValidationError("plan_invalid_markers")
    return CleaningOperation(name=name, markers=tuple(markers))
