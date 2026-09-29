"""Modelos no clínicos sincronizados con el contrato compartido v1.

No contienen reglas de diagnóstico, umbrales clínicos ni recomendaciones.
"""

from datetime import datetime
from enum import StrEnum
from math import isfinite

from pydantic import BaseModel, ConfigDict, Field, field_validator


CONTRACT_VERSION = "v1"
IDENTIFIER_PATTERN = r"^[a-z][a-z0-9-]{2,63}$"


class MetricCategory(StrEnum):
    """Categorías de organización visual, sin interpretación clínica."""

    ACTIVITY = "activity"
    REST = "rest"
    HYDRATION = "hydration"
    WELLBEING = "wellbeing"


class MeasurementSource(StrEnum):
    """Origen declarado de una medición."""

    MANUAL = "manual"
    SYNTHETIC = "synthetic"


class FixtureMetadata(BaseModel):
    """Metadatos requeridos para un fixture local reproducible."""

    model_config = ConfigDict(extra="forbid")

    contractVersion: str = Field(pattern="^v1$")
    source: str = Field(pattern="^synthetic-fixture$")
    generatedAt: datetime
    notice: str = Field(min_length=1)


class HealthProfile(BaseModel):
    """Perfil de demostración; no representa una cuenta autenticada."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=IDENTIFIER_PATTERN)
    displayName: str = Field(min_length=1, max_length=80)


class MetricDefinition(BaseModel):
    """Definición técnica de una métrica para visualización futura."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=IDENTIFIER_PATTERN)
    label: str = Field(min_length=1, max_length=80)
    unit: str = Field(min_length=1, max_length=24)
    category: MetricCategory


class Measurement(BaseModel):
    """Registro de valor y fecha, sin interpretación del valor."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=IDENTIFIER_PATTERN)
    metricId: str = Field(pattern=IDENTIFIER_PATTERN)
    value: float
    recordedAt: datetime
    source: MeasurementSource

    @field_validator("value")
    @classmethod
    def value_must_be_finite(cls, value: float) -> float:
        """Rechaza valores no serializables sin interpretar su significado."""
        if not isfinite(value):
            raise ValueError("value must be finite")
        return value


class MeasurementCreate(BaseModel):
    """Entrada técnica para añadir una medición manual a la demo local."""

    model_config = ConfigDict(extra="forbid")

    metricId: str = Field(pattern=IDENTIFIER_PATTERN)
    value: float
    recordedAt: datetime

    @field_validator("value")
    @classmethod
    def value_must_be_finite(cls, value: float) -> float:
        """Evita valores no serializables sin definir rangos clínicos."""
        if not isfinite(value):
            raise ValueError("value must be finite")
        return value


class HealthDashboardFixture(BaseModel):
    """Representación tipada del archivo de fixture v1."""

    model_config = ConfigDict(extra="forbid")

    metadata: FixtureMetadata
    profile: HealthProfile
    metrics: list[MetricDefinition] = Field(min_length=1)
    measurements: list[Measurement]


class ErrorResponse(BaseModel):
    """Error HTTP estable que no incluye valores ni identificadores sensibles."""

    model_config = ConfigDict(extra="forbid")

    code: str = Field(pattern=r"^[a-z][a-z0-9_]{2,63}$")
    message: str = Field(min_length=1, max_length=160)
    details: list[str] = Field(default_factory=list)
