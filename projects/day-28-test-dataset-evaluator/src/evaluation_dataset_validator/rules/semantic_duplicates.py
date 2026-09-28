"""Detección local de entradas textuales semánticamente equivalentes."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from collections.abc import Iterable

from evaluation_dataset_validator.models.contracts import (
    DatasetRecord,
    Severity,
    ValidationIssue,
)


class SemanticDuplicateInputRule:
    """Reporta repeticiones de entradas textuales normalizadas mediante SHA-256."""

    name = "semantic_duplicate_input"

    def __init__(self, duplicate_record_ids: set[str], severity: Severity) -> None:
        self.duplicate_record_ids = duplicate_record_ids
        self.severity = severity

    @classmethod
    def from_records(
        cls, records: Iterable[DatasetRecord], severity: Severity
    ) -> "SemanticDuplicateInputRule":
        """Build a stateless per-record rule from deterministic input fingerprints."""
        seen_fingerprints: set[str] = set()
        duplicate_record_ids: set[str] = set()
        for record in records:
            fingerprint = fingerprint_text_input(record.input)
            if fingerprint is None:
                continue
            if fingerprint in seen_fingerprints:
                duplicate_record_ids.add(record.id)
            else:
                seen_fingerprints.add(fingerprint)
        return cls(duplicate_record_ids, severity)

    def evaluate(self, record: DatasetRecord) -> list[ValidationIssue]:
        """Return a warning or error for each repeated normalized text input."""
        if record.id not in self.duplicate_record_ids:
            return []
        return [
            ValidationIssue(
                code="semantic_duplicate_input",
                message="La entrada coincide con una entrada textual anterior tras normalizarla.",
                severity=self.severity,
                record_id=record.id,
                field="input",
                rule=self.name,
            )
        ]


def fingerprint_text_input(value: object) -> str | None:
    """Return a stable digest for non-blank strings; ignore non-text inputs by design."""
    if not isinstance(value, str):
        return None
    normalized = _normalize_text(value)
    if not normalized:
        return None
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _normalize_text(value: str) -> str:
    """Normalize Unicode, case and whitespace without attempting linguistic inference."""
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return re.sub(r"\s+", " ", normalized).strip()
