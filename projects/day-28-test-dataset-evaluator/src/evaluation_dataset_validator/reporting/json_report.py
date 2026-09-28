"""Serialización estable de informes hacia JSON."""

from __future__ import annotations

import json
from pathlib import Path

from evaluation_dataset_validator.models.contracts import ValidationReport


def write_json_report(report: ValidationReport, destination: Path) -> None:
    """Persist a UTF-8, human-readable validation report."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
