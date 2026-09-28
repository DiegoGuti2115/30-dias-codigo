"""Renderizadores locales opcionales para informes de validación."""

from __future__ import annotations

import csv
import json
from io import StringIO
from pathlib import Path
from typing import TextIO

from evaluation_dataset_validator.models.contracts import ValidationReport


def write_console_report(report: ValidationReport, stream: TextIO) -> None:
    """Write a concise, deterministic human-readable report."""
    summary = report.summary
    stream.write(
        "Resumen: "
        f"{summary.total_records} registros, {summary.error_count} errores, "
        f"{summary.warning_count} advertencias. Válido: {report.is_valid}.\n"
    )
    for field, counts in summary.coverage_by_field.items():
        formatted_counts = ", ".join(f"{value}={count}" for value, count in counts.items())
        stream.write(f"Cobertura {field}: {formatted_counts or 'sin valores observados'}.\n")
    for issue in report.issues:
        location = ""
        if issue.location is not None:
            location = f" [{issue.location.file}:{issue.location.line}:{issue.location.column}]"
        record = f" ({issue.record_id})" if issue.record_id else ""
        stream.write(f"{issue.severity.upper()} {issue.code}{record}{location}: {issue.message}\n")


def write_csv_report(report: ValidationReport, destination: Path) -> None:
    """Persist issues as a portable UTF-8 CSV table."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    buffer = StringIO(newline="")
    writer = csv.DictWriter(
        buffer,
        fieldnames=("code", "message", "severity", "record_id", "field", "rule", "file", "line", "column"),
    )
    writer.writeheader()
    for issue in report.issues:
        writer.writerow(
            {
                "code": issue.code,
                "message": issue.message,
                "severity": issue.severity,
                "record_id": issue.record_id or "",
                "field": issue.field or "",
                "rule": issue.rule,
                "file": issue.location.file if issue.location else "",
                "line": issue.location.line if issue.location else "",
                "column": issue.location.column if issue.location else "",
            }
        )
    destination.write_text(buffer.getvalue(), encoding="utf-8", newline="")


def write_sarif_report(report: ValidationReport, destination: Path) -> None:
    """Persist a SARIF 2.1.0 report compatible with static-analysis viewers."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    rules = {
        issue.code: {
            "id": issue.code,
            "shortDescription": {"text": issue.rule},
            "fullDescription": {"text": issue.message},
        }
        for issue in report.issues
    }
    results = []
    for issue in report.issues:
        result = {
            "ruleId": issue.code,
            "level": "error" if issue.severity == "error" else "warning",
            "message": {"text": issue.message},
        }
        if issue.location is not None:
            result["locations"] = [
                {
                    "physicalLocation": {
                        "artifactLocation": {"uri": issue.location.file},
                        "region": {
                            "startLine": issue.location.line,
                            "startColumn": issue.location.column,
                        },
                    }
                }
            ]
        results.append(result)
    payload = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{"tool": {"driver": {"name": "evaluation-dataset-validator", "rules": list(rules.values())}}, "results": results}],
    }
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
