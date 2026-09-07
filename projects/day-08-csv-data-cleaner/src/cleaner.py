"""Pure, deterministic v1 transformations for validated CSV datasets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from csv_profile import CsvContractError, CsvDataset, StructuralProfile, profile_csv, validate_normalized_headers
from plan import CleaningPlan


@dataclass(frozen=True)
class CleaningResult:
    """The internal result consumed by future CSV and JSON publication code."""

    source: dict[str, object]
    plan: dict[str, object]
    profile_before: StructuralProfile
    profile_after: StructuralProfile
    operation_results: tuple[dict[str, int | str], ...]
    headers: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]

    @property
    def warnings(self) -> list[str]:
        return (
            ["formula_like_cells_present"]
            if self.profile_after.formula_like_cell_count > 0
            else []
        )

    def summary(self) -> dict[str, Any]:
        """Build the deterministic v1 summary without writing files."""

        return {
            "status": "success",
            "source": self.source,
            "plan": self.plan,
            "profile_before": self.profile_before.as_dict(),
            "profile_after": self.profile_after.as_dict(),
            "operations": list(self.operation_results),
            "warnings": self.warnings,
        }


def clean_dataset(dataset: CsvDataset, plan: CleaningPlan) -> CleaningResult:
    """Apply a validated plan in contractual order to an in-memory dataset."""

    profile_before = profile_csv(dataset.headers, dataset.rows)
    headers = dataset.headers
    rows = list(dataset.rows)
    operation_results: list[dict[str, int | str]] = []

    for operation in plan.operations:
        if operation.name == "normalize_headers":
            normalized = validate_normalized_headers(headers)
            operation_results.append(
                {
                    "operation": operation.name,
                    "headers_changed": sum(old != new for old, new in zip(headers, normalized)),
                }
            )
            headers = normalized
        elif operation.name == "drop_empty_rows":
            retained = [row for row in rows if not all(cell == "" for cell in row)]
            operation_results.append(
                {"operation": operation.name, "rows_removed": len(rows) - len(retained)}
            )
            rows = retained
        elif operation.name == "trim_fields":
            trimmed = [tuple(cell.strip() for cell in row) for row in rows]
            operation_results.append(
                {
                    "operation": operation.name,
                    "fields_changed": sum(
                        old != new
                        for original, cleaned in zip(rows, trimmed)
                        for old, new in zip(original, cleaned)
                    ),
                }
            )
            rows = trimmed
        elif operation.name == "replace_missing_markers":
            markers = set(operation.markers)
            replaced = [
                tuple("" if cell in markers else cell for cell in row)
                for row in rows
            ]
            operation_results.append(
                {
                    "operation": operation.name,
                    "fields_replaced": sum(
                        cell in markers for row in rows for cell in row
                    ),
                }
            )
            rows = replaced
        elif operation.name == "drop_exact_duplicates":
            seen: set[tuple[str, ...]] = set()
            retained = []
            for row in rows:
                if row not in seen:
                    seen.add(row)
                    retained.append(row)
            operation_results.append(
                {"operation": operation.name, "rows_removed": len(rows) - len(retained)}
            )
            rows = retained
        else:  # Defensive protection if a future caller circumvents plan validation.
            raise CsvContractError("plan_unknown_operation")

    frozen_rows = tuple(rows)
    profile_after = profile_csv(headers, frozen_rows)
    return CleaningResult(
        source={
            "file_name": dataset.source_name,
            "size_bytes": dataset.size_bytes,
            "data_row_count": dataset.data_row_count,
            "column_count": dataset.column_count,
        },
        plan={"version": plan.version, "requested_operations": list(plan.requested_operations)},
        profile_before=profile_before,
        profile_after=profile_after,
        operation_results=tuple(operation_results),
        headers=headers,
        rows=frozen_rows,
    )
