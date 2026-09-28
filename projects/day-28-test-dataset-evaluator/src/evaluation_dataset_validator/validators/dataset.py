"""Orquestación determinista de validaciones de esquema y reglas."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from typing import Any

from pydantic import ValidationError as PydanticValidationError

from evaluation_dataset_validator.config.settings import ValidationSettings
from evaluation_dataset_validator.models.contracts import (
    DatasetRecord,
    Severity,
    SourceLocation,
    ValidationIssue,
    ValidationReport,
    ValidationSummary,
)
from evaluation_dataset_validator.rules.base import ValidationRule
from evaluation_dataset_validator.rules.content import EmptyStringRule
from evaluation_dataset_validator.rules.evaluation_tasks import (
    CoverageRule,
    EvaluationTaskSchemaRule,
    TrainEvaluationLeakageRule,
    coverage_counts,
)
from evaluation_dataset_validator.rules.metadata import EmptyMetadataRule
from evaluation_dataset_validator.rules.semantic_duplicates import SemanticDuplicateInputRule
from evaluation_dataset_validator.rules.task_metadata import RequiredMetadataFieldsRule
from evaluation_dataset_validator.services.dataset_loader import SourceRecord


class DatasetValidator:
    """Valida registros compatibles y conserva sus ubicaciones de origen."""

    def __init__(
        self,
        settings: ValidationSettings | None = None,
        rules: Iterable[ValidationRule] | None = None,
    ) -> None:
        self.settings = settings or ValidationSettings()
        self.custom_rules = tuple(rules) if rules is not None else None

    def validate(self, payload: Iterable[Any | SourceRecord]) -> ValidationReport:
        """Return a complete report without raising for invalid source records."""
        issues: list[ValidationIssue] = []
        valid_records: list[DatasetRecord] = []
        record_locations: list[SourceLocation] = []
        total_records = 0
        for position, item in enumerate(payload):
            total_records += 1
            raw_record, location = self._source_payload(item, position)
            try:
                record = DatasetRecord.model_validate(raw_record)
                valid_records.append(record)
                record_locations.append(location)
            except PydanticValidationError as error:
                issues.append(self._schema_issue(position, error, location))

        if self.settings.is_rule_enabled("unique_id"):
            issues.extend(self._duplicate_id_issues(valid_records, record_locations))

        rules, global_rules = self._rules_for(valid_records)
        for rule in global_rules:
            issues.extend(rule.global_issues())
        for record, location in zip(valid_records, record_locations, strict=True):
            for rule in rules:
                issues.extend(self._with_location(rule.evaluate(record), location))

        error_count = sum(issue.severity is Severity.ERROR for issue in issues)
        warning_count = sum(issue.severity is Severity.WARNING for issue in issues)
        invalid_ids = {issue.record_id for issue in issues if issue.severity is Severity.ERROR}
        summary = ValidationSummary(
            total_records=total_records,
            valid_records=sum(record.id not in invalid_ids for record in valid_records),
            error_count=error_count,
            warning_count=warning_count,
            issues_by_code=dict(sorted(Counter(issue.code for issue in issues).items())),
            issues_by_task=self._issues_by_metadata(issues, valid_records, "task"),
            issues_by_partition=self._issues_by_metadata(issues, valid_records, "partition"),
            coverage_by_field=coverage_counts(valid_records, self.settings.coverage_required_values),
        )
        return ValidationReport(
            is_valid=error_count == 0,
            summary=summary,
            issues=issues[: self.settings.max_issues],
        )

    @staticmethod
    def _source_payload(item: Any | SourceRecord, position: int) -> tuple[Any, SourceLocation]:
        if isinstance(item, SourceRecord):
            return item.payload, item.location
        return item, SourceLocation(file="<memoria>", line=position + 1, column=1)

    @staticmethod
    def _with_location(
        issues: list[ValidationIssue], location: SourceLocation
    ) -> list[ValidationIssue]:
        return [issue.model_copy(update={"location": location}) for issue in issues]

    @staticmethod
    def _issues_by_metadata(
        issues: list[ValidationIssue], records: list[DatasetRecord], metadata_key: str
    ) -> dict[str, int]:
        values_by_id = {
            record.id: str(record.metadata.get(metadata_key, "sin_definir")) for record in records
        }
        counts = Counter(
            values_by_id.get(issue.record_id, "sin_definir")
            for issue in issues
            if issue.record_id is not None
        )
        return dict(sorted(counts.items()))

    def _rules_for(
        self, records: list[DatasetRecord]
    ) -> tuple[tuple[ValidationRule, ...], tuple[CoverageRule, ...]]:
        if self.custom_rules is not None:
            return self.custom_rules, ()
        rules: list[ValidationRule] = []
        global_rules: list[CoverageRule] = []
        if self.settings.is_rule_enabled("empty_metadata"):
            rules.append(EmptyMetadataRule(self.settings.severity_for("empty_metadata")))
        if self.settings.is_rule_enabled("empty_input"):
            rules.append(EmptyStringRule("input", self.settings.severity_for("empty_input")))
        if self.settings.is_rule_enabled("empty_expected_output"):
            rules.append(
                EmptyStringRule(
                    "expected_output",
                    self.settings.severity_for("empty_expected_output"),
                )
            )
        if self.settings.is_rule_enabled("required_metadata_fields"):
            rules.append(
                RequiredMetadataFieldsRule(
                    self.settings.metadata_required_fields_by_task,
                    self.settings.severity_for("required_metadata_fields"),
                )
            )
        if self.settings.is_rule_enabled("semantic_duplicate_input"):
            rules.append(
                SemanticDuplicateInputRule.from_records(
                    records,
                    self.settings.severity_for("semantic_duplicate_input"),
                )
            )
        if self.settings.is_rule_enabled("evaluation_task_schema"):
            rules.append(
                EvaluationTaskSchemaRule(
                    self.settings.supported_task_schemas,
                    self.settings.severity_for("evaluation_task_schema"),
                )
            )
        if self.settings.is_rule_enabled("coverage"):
            global_rules.append(
                CoverageRule.from_records(
                    records,
                    self.settings.coverage_required_values,
                    self.settings.severity_for("coverage"),
                )
            )
        if self.settings.is_rule_enabled("train_evaluation_leakage"):
            rules.append(
                TrainEvaluationLeakageRule.from_records(
                    records,
                    self.settings.leakage_hash_fields,
                    self.settings.leakage_train_partitions,
                    self.settings.leakage_evaluation_partitions,
                    self.settings.severity_for("train_evaluation_leakage"),
                )
            )
        return tuple(rules), tuple(global_rules)

    def _duplicate_id_issues(
        self, records: list[DatasetRecord], locations: list[SourceLocation]
    ) -> list[ValidationIssue]:
        counts = Counter(record.id for record in records)
        return [
            ValidationIssue(
                code="duplicate_id",
                message="El identificador aparece más de una vez en el dataset.",
                severity=self.settings.severity_for("unique_id"),
                record_id=record.id,
                field="id",
                rule="unique_id",
                location=location,
            )
            for record, location in zip(records, locations, strict=True)
            if counts[record.id] > 1
        ]

    @staticmethod
    def _schema_issue(
        position: int, error: PydanticValidationError, location: SourceLocation
    ) -> ValidationIssue:
        return ValidationIssue(
            code="invalid_schema",
            message=(
                f"El registro en la posición {position} no cumple el esquema: "
                f"{error.errors()[0]['msg']}"
            ),
            severity=Severity.ERROR,
            field=str(error.errors()[0]["loc"][-1]),
            rule="schema",
            location=location,
        )
