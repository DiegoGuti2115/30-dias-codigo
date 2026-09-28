"""Reglas iniciales relacionadas con la trazabilidad del registro."""

from __future__ import annotations

from evaluation_dataset_validator.models.contracts import (
    DatasetRecord,
    Severity,
    ValidationIssue,
)


class EmptyMetadataRule:
    """Advierte cuando un caso no aporta contexto auxiliar reproducible."""

    name = "empty_metadata"

    def __init__(self, severity: Severity) -> None:
        self.severity = severity

    def evaluate(self, record: DatasetRecord) -> list[ValidationIssue]:
        """Report a warning when the optional metadata object is empty."""
        if record.metadata:
            return []
        return [
            ValidationIssue(
                code="empty_metadata",
                message="El registro no incluye metadatos para su trazabilidad.",
                severity=self.severity,
                record_id=record.id,
                field="metadata",
                rule=self.name,
            )
        ]
