"""Configuración explícita y local del proceso de validación."""

from __future__ import annotations

from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

from evaluation_dataset_validator.models.contracts import Severity


class ValidationSettings(BaseModel):
    """Opciones locales que activan, desactivan y priorizan reglas de validación."""

    model_config = ConfigDict(extra="forbid")

    RULE_NAMES: ClassVar[frozenset[str]] = frozenset(
        {
            "unique_id",
            "empty_metadata",
            "empty_input",
            "empty_expected_output",
            "required_metadata_fields",
            "semantic_duplicate_input",
            "evaluation_task_schema",
            "coverage",
            "train_evaluation_leakage",
        }
    )
    DEFAULT_SEVERITIES: ClassVar[dict[str, Severity]] = {
        "unique_id": Severity.ERROR,
        "empty_metadata": Severity.WARNING,
        "empty_input": Severity.ERROR,
        "empty_expected_output": Severity.ERROR,
        "required_metadata_fields": Severity.ERROR,
        "semantic_duplicate_input": Severity.WARNING,
        "evaluation_task_schema": Severity.ERROR,
        "coverage": Severity.WARNING,
        "train_evaluation_leakage": Severity.WARNING,
    }

    required_fields: tuple[str, ...] = ("id", "input", "expected_output")
    require_unique_ids: bool = True
    warn_on_empty_metadata: bool = True
    detect_semantic_duplicates: bool = True
    metadata_required_fields_by_task: dict[str, tuple[str, ...]] = Field(default_factory=dict)
    supported_task_schemas: tuple[str, ...] = (
        "text/v1",
        "classification/v1",
        "extraction/v1",
        "conversation/v1",
    )
    coverage_required_values: dict[str, tuple[str, ...]] = Field(default_factory=dict)
    leakage_hash_fields: tuple[str, ...] = ()
    leakage_train_partitions: tuple[str, ...] = ("train",)
    leakage_evaluation_partitions: tuple[str, ...] = ("validation", "test", "evaluation")
    disabled_rules: tuple[str, ...] = ()
    rule_severities: dict[str, Severity] = Field(
        default_factory=lambda: ValidationSettings.DEFAULT_SEVERITIES.copy()
    )
    max_issues: int = Field(default=100, ge=1)

    @field_validator("required_fields")
    @classmethod
    def validate_required_fields(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        """Keep the minimum dataset contract explicit and unambiguous."""
        expected_fields = ("id", "input", "expected_output")
        if value != expected_fields:
            raise ValueError(
                "required_fields debe ser exactamente ['id', 'input', 'expected_output']"
            )
        return value

    @field_validator("disabled_rules")
    @classmethod
    def validate_disabled_rules(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        """Reject unknown or repeated rule names before validation starts."""
        cls._validate_rule_names(value)
        if len(set(value)) != len(value):
            raise ValueError("disabled_rules no puede contener reglas repetidas")
        return value

    @field_validator("rule_severities", mode="before")
    @classmethod
    def merge_rule_severities(cls, value: object) -> dict[str, object]:
        """Merge explicit severity overrides with the stable defaults."""
        if not isinstance(value, dict):
            return value  # type: ignore[return-value]
        return cls.DEFAULT_SEVERITIES | value

    @field_validator("rule_severities")
    @classmethod
    def validate_rule_severities(
        cls, value: dict[str, Severity]
    ) -> dict[str, Severity]:
        """Reject unknown severity configuration keys after applying defaults."""
        cls._validate_rule_names(tuple(value))
        return value

    @field_validator("metadata_required_fields_by_task")
    @classmethod
    def validate_metadata_requirements(
        cls, value: dict[str, tuple[str, ...]]
    ) -> dict[str, tuple[str, ...]]:
        """Ensure task names and required metadata keys are usable strings."""
        for task, fields in value.items():
            if not task.strip():
                raise ValueError("metadata_required_fields_by_task no admite tareas vacías")
            if not fields:
                raise ValueError(f"la tarea '{task}' debe requerir al menos un campo")
            if any(not field.strip() for field in fields):
                raise ValueError(f"la tarea '{task}' contiene un campo de metadatos vacío")
            if len(set(fields)) != len(fields):
                raise ValueError(f"la tarea '{task}' contiene campos de metadatos repetidos")
        return value

    @field_validator("supported_task_schemas")
    @classmethod
    def validate_task_schemas(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        """Accept only the local, explicitly versioned task contracts."""
        allowed_schemas = {"text/v1", "classification/v1", "extraction/v1", "conversation/v1"}
        if not value or len(set(value)) != len(value) or set(value).difference(allowed_schemas):
            raise ValueError("supported_task_schemas debe usar esquemas locales únicos como 'text/v1'")
        return value

    @field_validator("coverage_required_values")
    @classmethod
    def validate_coverage_requirements(
        cls, value: dict[str, tuple[str, ...]]
    ) -> dict[str, tuple[str, ...]]:
        """Keep coverage targets explicit and scoped to stable record or metadata paths."""
        for field_name, expected_values in value.items():
            if field_name not in {"metadata.class", "metadata.language", "metadata.category", "metadata.partition"}:
                raise ValueError(f"campo de cobertura no compatible: '{field_name}'")
            if not expected_values or any(not item.strip() for item in expected_values):
                raise ValueError(f"el campo de cobertura '{field_name}' requiere valores no vacíos")
            if len(set(expected_values)) != len(expected_values):
                raise ValueError(f"el campo de cobertura '{field_name}' contiene valores repetidos")
        return value

    @field_validator("leakage_hash_fields")
    @classmethod
    def validate_leakage_hash_fields(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        """Restrict leakage fingerprints to deterministic, documented record paths."""
        allowed_fields = {"input", "expected_output", "metadata.source_id"}
        if len(set(value)) != len(value) or set(value).difference(allowed_fields):
            raise ValueError("leakage_hash_fields solo admite input, expected_output o metadata.source_id")
        return value

    @field_validator("leakage_train_partitions", "leakage_evaluation_partitions")
    @classmethod
    def validate_partitions(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        """Ensure partition groups are non-empty labels before global comparison starts."""
        if not value or any(not partition.strip() for partition in value):
            raise ValueError("las particiones de fugas deben contener etiquetas no vacías")
        if len(set(value)) != len(value):
            raise ValueError("las particiones de fugas no pueden repetirse")
        return value

    def is_rule_enabled(self, rule_name: str) -> bool:
        """Return whether a named rule should be included in the current run."""
        if rule_name in self.disabled_rules:
            return False
        if rule_name == "unique_id":
            return self.require_unique_ids
        if rule_name == "empty_metadata":
            return self.warn_on_empty_metadata
        if rule_name == "semantic_duplicate_input":
            return self.detect_semantic_duplicates
        if rule_name == "coverage":
            return bool(self.coverage_required_values)
        if rule_name == "train_evaluation_leakage":
            return bool(self.leakage_hash_fields)
        return True

    def severity_for(self, rule_name: str) -> Severity:
        """Return the configured severity for a supported, enabled rule."""
        return self.rule_severities[rule_name]

    @classmethod
    def _validate_rule_names(cls, rule_names: tuple[str, ...]) -> None:
        unknown_rules = set(rule_names).difference(cls.RULE_NAMES)
        if unknown_rules:
            raise ValueError(
                f"reglas desconocidas: {', '.join(sorted(unknown_rules))}"
            )
