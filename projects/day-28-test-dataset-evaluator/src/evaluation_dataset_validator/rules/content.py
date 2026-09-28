"""Reglas de calidad para valores textuales de entrada y salida."""

from __future__ import annotations

from evaluation_dataset_validator.models.contracts import (
    DatasetRecord,
    Severity,
    ValidationIssue,
)


class EmptyStringRule:
    """Detecta cadenas vacías o compuestas solo por espacios en un campo concreto."""

    def __init__(self, field_name: str, severity: Severity) -> None:
        self.field_name = field_name
        self.severity = severity
        self.name = f"empty_{field_name}"

    def evaluate(self, record: DatasetRecord) -> list[ValidationIssue]:
        """Return one issue only when the configured field is an empty string."""
        value = getattr(record, self.field_name)
        if not isinstance(value, str) or value.strip():
            return []
        return [
            ValidationIssue(
                code=self.name,
                message=f"El campo '{self.field_name}' no puede ser una cadena vacía.",
                severity=self.severity,
                record_id=record.id,
                field=self.field_name,
                rule=self.name,
            )
        ]
