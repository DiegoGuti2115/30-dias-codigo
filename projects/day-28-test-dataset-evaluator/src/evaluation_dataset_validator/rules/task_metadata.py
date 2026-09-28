"""Regla de campos de metadatos requeridos por tipo de tarea."""

from __future__ import annotations

from evaluation_dataset_validator.models.contracts import (
    DatasetRecord,
    Severity,
    ValidationIssue,
)


class RequiredMetadataFieldsRule:
    """Exige claves de metadata para registros que declaran una tarea conocida."""

    name = "required_metadata_fields"

    def __init__(
        self, required_fields_by_task: dict[str, tuple[str, ...]], severity: Severity
    ) -> None:
        self.required_fields_by_task = required_fields_by_task
        self.severity = severity

    def evaluate(self, record: DatasetRecord) -> list[ValidationIssue]:
        """Return one issue per missing or blank metadata field for the record task."""
        task = record.metadata.get("task")
        if not isinstance(task, str):
            return []
        required_fields = self.required_fields_by_task.get(task)
        if required_fields is None:
            return []
        return [
            ValidationIssue(
                code="missing_required_metadata",
                message=(
                    f"La tarea '{task}' requiere el metadato '{field_name}' no vacío."
                ),
                severity=self.severity,
                record_id=record.id,
                field=f"metadata.{field_name}",
                rule=self.name,
            )
            for field_name in required_fields
            if not _has_non_empty_value(record.metadata, field_name)
        ]


def _has_non_empty_value(metadata: dict[str, object], field_name: str) -> bool:
    """Treat absent values and blank strings as missing, preserving other JSON values."""
    if field_name not in metadata:
        return False
    value = metadata[field_name]
    return not isinstance(value, str) or bool(value.strip())
