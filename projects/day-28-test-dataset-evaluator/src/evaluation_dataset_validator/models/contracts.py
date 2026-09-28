"""Contratos Pydantic del dominio y de los informes del validador."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Severity(StrEnum):
    """Niveles de severidad ordenados para los hallazgos."""

    ERROR = "error"
    WARNING = "warning"


class SourceLocation(BaseModel):
    """Ubicación física reproducible de un registro dentro de su archivo origen."""

    file: str = Field(min_length=1)
    line: int = Field(ge=1)
    column: int = Field(ge=1)


class DatasetRecord(BaseModel):
    """Registro mínimo de un caso de evaluación independiente."""

    model_config = ConfigDict(extra="allow")

    id: str = Field(min_length=1, description="Identificador único y estable del caso.")
    input: Any = Field(description="Entrada enviada al sistema evaluado.")
    expected_output: Any = Field(description="Resultado esperado para la evaluación.")
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("id")
    @classmethod
    def validate_identifier(cls, value: str) -> str:
        """Reject blank identifiers while preserving the source identifier."""
        if not value.strip():
            raise ValueError("El identificador no puede contener solo espacios.")
        return value


class ValidationIssue(BaseModel):
    """Hallazgo normalizado producido por una regla de validación."""

    code: str = Field(min_length=1)
    message: str = Field(min_length=1)
    severity: Severity
    record_id: str | None = None
    field: str | None = None
    rule: str = Field(min_length=1)
    location: SourceLocation | None = None


class ValidationSummary(BaseModel):
    """Contadores agregados para interpretar un informe de validación."""

    total_records: int = Field(ge=0)
    valid_records: int = Field(ge=0)
    error_count: int = Field(ge=0)
    warning_count: int = Field(ge=0)
    issues_by_code: dict[str, int] = Field(default_factory=dict)
    issues_by_task: dict[str, int] = Field(default_factory=dict)
    issues_by_partition: dict[str, int] = Field(default_factory=dict)
    coverage_by_field: dict[str, dict[str, int]] = Field(default_factory=dict)


class ValidationReport(BaseModel):
    """Salida serializable y determinista de una ejecución de validación."""

    is_valid: bool
    summary: ValidationSummary
    issues: list[ValidationIssue] = Field(default_factory=list)
