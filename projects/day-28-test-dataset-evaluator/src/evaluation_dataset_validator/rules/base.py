"""Protocolo para reglas independientes y extensibles."""

from __future__ import annotations

from typing import Protocol

from evaluation_dataset_validator.models.contracts import DatasetRecord, ValidationIssue


class ValidationRule(Protocol):
    """Contrato que deben cumplir las reglas aplicadas a cada registro válido."""

    name: str

    def evaluate(self, record: DatasetRecord) -> list[ValidationIssue]:
        """Devuelve los hallazgos producidos para un registro."""
