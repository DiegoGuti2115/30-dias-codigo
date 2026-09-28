"""Reglas locales para contratos versionados de evaluación de IA."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Iterable
from typing import Any

from evaluation_dataset_validator.models.contracts import (
    DatasetRecord,
    Severity,
    ValidationIssue,
)


class EvaluationTaskSchemaRule:
    """Valida los campos declarados por un esquema de tarea versionado."""

    name = "evaluation_task_schema"

    def __init__(self, supported_schemas: tuple[str, ...], severity: Severity) -> None:
        self.supported_schemas = set(supported_schemas)
        self.severity = severity

    def evaluate(self, record: DatasetRecord) -> list[ValidationIssue]:
        """Validate only records that explicitly opt into a phase-four task schema."""
        schema = record.metadata.get("task_schema")
        if schema is None:
            return []
        if not isinstance(schema, str) or schema not in self.supported_schemas:
            return [self._issue(record, "unsupported_task_schema", "metadata.task_schema", "El esquema de tarea no está soportado por la configuración.")]

        validator = {
            "text/v1": self._validate_text,
            "classification/v1": self._validate_classification,
            "extraction/v1": self._validate_extraction,
            "conversation/v1": self._validate_conversation,
        }[schema]
        return validator(record)

    def _validate_text(self, record: DatasetRecord) -> list[ValidationIssue]:
        return self._expected_evaluator(record, {"exact_match", "contains"}, str)

    def _validate_classification(self, record: DatasetRecord) -> list[ValidationIssue]:
        issues = self._expected_evaluator(record, {"label_match"}, str)
        labels = record.metadata.get("label_set")
        if not isinstance(labels, list) or not labels or not all(isinstance(label, str) and label.strip() for label in labels):
            issues.append(self._issue(record, "invalid_evaluation_schema", "metadata.label_set", "El esquema classification/v1 requiere metadata.label_set como lista no vacía de etiquetas."))
        elif record.expected_output not in labels:
            issues.append(self._issue(record, "invalid_evaluation_schema", "expected_output", "expected_output debe pertenecer a metadata.label_set para classification/v1."))
        return issues

    def _validate_extraction(self, record: DatasetRecord) -> list[ValidationIssue]:
        issues = self._expected_evaluator(record, {"field_match"}, (dict, list))
        fields = record.metadata.get("extraction_fields")
        if not isinstance(fields, list) or not fields or not all(isinstance(field, str) and field.strip() for field in fields):
            issues.append(self._issue(record, "invalid_evaluation_schema", "metadata.extraction_fields", "El esquema extraction/v1 requiere metadata.extraction_fields como lista no vacía."))
        return issues

    def _validate_conversation(self, record: DatasetRecord) -> list[ValidationIssue]:
        issues = self._expected_evaluator(record, {"turn_match"}, str)
        if not isinstance(record.input, list) or not record.input:
            issues.append(self._issue(record, "invalid_evaluation_schema", "input", "El esquema conversation/v1 requiere input como una lista no vacía de turnos."))
            return issues
        for turn in record.input:
            if not isinstance(turn, dict) or not isinstance(turn.get("role"), str) or not isinstance(turn.get("content"), str) or not turn["role"].strip() or not turn["content"].strip():
                issues.append(self._issue(record, "invalid_evaluation_schema", "input", "Cada turno de conversation/v1 requiere role y content como cadenas no vacías."))
                break
        return issues

    def _expected_evaluator(
        self, record: DatasetRecord, accepted_evaluators: set[str], output_type: type | tuple[type, ...]
    ) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        evaluator = record.metadata.get("evaluator")
        if evaluator not in accepted_evaluators:
            expected = ", ".join(sorted(accepted_evaluators))
            issues.append(self._issue(record, "invalid_evaluator", "metadata.evaluator", f"El esquema requiere metadata.evaluator: {expected}."))
        if not isinstance(record.expected_output, output_type):
            issues.append(self._issue(record, "invalid_evaluation_schema", "expected_output", "expected_output no tiene el tipo esperado por el esquema de tarea."))
        return issues

    def _issue(self, record: DatasetRecord, code: str, field: str, message: str) -> ValidationIssue:
        return ValidationIssue(code=code, message=message, severity=self.severity, record_id=record.id, field=field, rule=self.name)


class CoverageRule:
    """Reporta valores configurados que no aparecen en metadatos del dataset."""

    name = "coverage"

    def __init__(self, missing_values_by_field: dict[str, tuple[str, ...]], severity: Severity) -> None:
        self.missing_values_by_field = missing_values_by_field
        self.severity = severity

    @classmethod
    def from_records(
        cls, records: Iterable[DatasetRecord], required_values: dict[str, tuple[str, ...]], severity: Severity
    ) -> "CoverageRule":
        observed: dict[str, set[str]] = {field: set() for field in required_values}
        for record in records:
            for field in observed:
                value = _metadata_value(record, field)
                if isinstance(value, str) and value.strip():
                    observed[field].add(value)
        missing = {
            field: tuple(value for value in values if value not in observed[field])
            for field, values in required_values.items()
        }
        return cls({field: values for field, values in missing.items() if values}, severity)

    def evaluate(self, record: DatasetRecord) -> list[ValidationIssue]:
        """Emit global coverage findings only once, on the first valid record."""
        return []

    def global_issues(self) -> list[ValidationIssue]:
        return [
            ValidationIssue(code="missing_coverage", message=f"No hay registros con {field}='{value}'.", severity=self.severity, field=field, rule=self.name)
            for field, values in sorted(self.missing_values_by_field.items())
            for value in values
        ]


class TrainEvaluationLeakageRule:
    """Detecta coincidencias exactas entre particiones mediante huellas SHA-256 locales."""

    name = "train_evaluation_leakage"

    def __init__(self, leaked_ids: set[str], severity: Severity) -> None:
        self.leaked_ids = leaked_ids
        self.severity = severity

    @classmethod
    def from_records(
        cls, records: Iterable[DatasetRecord], hash_fields: tuple[str, ...], train_partitions: tuple[str, ...], evaluation_partitions: tuple[str, ...], severity: Severity
    ) -> "TrainEvaluationLeakageRule":
        train_hashes: set[str] = set()
        evaluation_records: list[tuple[str, tuple[str, ...]]] = []
        for record in records:
            fingerprints = tuple(filter(None, (_fingerprint(_record_value(record, field)) for field in hash_fields)))
            partition = record.metadata.get("partition")
            if partition in train_partitions:
                train_hashes.update(fingerprints)
            elif partition in evaluation_partitions:
                evaluation_records.append((record.id, fingerprints))
        return cls({record_id for record_id, fingerprints in evaluation_records if train_hashes.intersection(fingerprints)}, severity)

    def evaluate(self, record: DatasetRecord) -> list[ValidationIssue]:
        if record.id not in self.leaked_ids:
            return []
        return [ValidationIssue(code="train_evaluation_leakage", message="Una huella configurada coincide entre entrenamiento y evaluación.", severity=self.severity, record_id=record.id, field="metadata.partition", rule=self.name)]


def coverage_counts(records: Iterable[DatasetRecord], required_values: dict[str, tuple[str, ...]]) -> dict[str, dict[str, int]]:
    """Return deterministic coverage counters for configured dimensions and observed values."""
    counts: dict[str, Counter[str]] = {field: Counter() for field in required_values}
    for record in records:
        for field, counter in counts.items():
            value = _metadata_value(record, field)
            if isinstance(value, str) and value.strip():
                counter[value] += 1
    return {field: dict(sorted(counter.items())) for field, counter in sorted(counts.items())}


def _metadata_value(record: DatasetRecord, field: str) -> Any:
    return record.metadata.get(field.removeprefix("metadata."))


def _record_value(record: DatasetRecord, field: str) -> Any:
    if field.startswith("metadata."):
        return record.metadata.get(field.removeprefix("metadata."))
    return getattr(record, field)


def _fingerprint(value: Any) -> str | None:
    if value is None:
        return None
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
