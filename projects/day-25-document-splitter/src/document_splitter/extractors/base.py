"""Shared contracts for ordered document text extraction."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class DocumentExtractionError(RuntimeError):
    """Raised when a validated document cannot yield extractable text."""


@dataclass(frozen=True)
class ExtractedDocument:
    """Text obtained from a source document in its original reading order."""

    source: Path
    text: str


class DocumentExtractor(Protocol):
    """Interface implemented by a format-specific document extractor."""

    def extract(self, source: Path) -> ExtractedDocument:
        """Read ``source`` and return its non-empty text in reading order."""
