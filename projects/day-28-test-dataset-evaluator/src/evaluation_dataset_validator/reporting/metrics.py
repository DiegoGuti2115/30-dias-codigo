"""Exportación determinista de métricas para observabilidad local."""

from __future__ import annotations

import json
from pathlib import Path

from evaluation_dataset_validator.models.contracts import ValidationReport


def metrics_payload(report: ValidationReport) -> dict[str, object]:
    """Project the canonical report summary into stable automation-oriented metrics."""
    summary = report.summary
    return {
        "is_valid": report.is_valid,
        "total_records": summary.total_records,
        "valid_records": summary.valid_records,
        "error_count": summary.error_count,
        "warning_count": summary.warning_count,
        "issues_by_code": summary.issues_by_code,
        "issues_by_task": summary.issues_by_task,
        "issues_by_partition": summary.issues_by_partition,
        "coverage_by_field": summary.coverage_by_field,
    }


def write_json_metrics(report: ValidationReport, destination: Path) -> None:
    """Write metrics as UTF-8 JSON without modifying the canonical report."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(metrics_payload(report), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_prometheus_metrics(report: ValidationReport, destination: Path) -> None:
    """Write a dependency-free Prometheus text exposition for aggregate counters."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    summary = report.summary
    lines = [
        "# HELP evaluation_dataset_valid Whether the validation report has no error findings.",
        "# TYPE evaluation_dataset_valid gauge",
        f"evaluation_dataset_valid {int(report.is_valid)}",
        "# HELP evaluation_dataset_records Number of dataset records by validation state.",
        "# TYPE evaluation_dataset_records gauge",
        f'evaluation_dataset_records{{state="total"}} {summary.total_records}',
        f'evaluation_dataset_records{{state="valid"}} {summary.valid_records}',
        "# HELP evaluation_dataset_issues Number of validation findings.",
        "# TYPE evaluation_dataset_issues gauge",
        f'evaluation_dataset_issues{{severity="error"}} {summary.error_count}',
        f'evaluation_dataset_issues{{severity="warning"}} {summary.warning_count}',
    ]
    lines.extend(
        f'evaluation_dataset_issues_by_code{{code="{_escape_label(code)}"}} {count}'
        for code, count in summary.issues_by_code.items()
    )
    lines.extend(
        f'evaluation_dataset_coverage{{field="{_escape_label(field)}",value="{_escape_label(value)}"}} {count}'
        for field, values in summary.coverage_by_field.items()
        for value, count in values.items()
    )
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _escape_label(value: str) -> str:
    """Escape the limited Prometheus label syntax used by report-derived strings."""
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
