"""Stable domain models for traceable document-splitting results."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResultChunk:
    """A serialized chunk with its normalized-text range and source identity."""

    id: str
    index: int
    text: str
    start_char: int
    end_char: int


@dataclass(frozen=True)
class DocumentResult:
    """The complete deterministic result produced for one source document."""

    source: str
    document_id: str
    chunk_size: int
    overlap: int
    chunks: tuple[ResultChunk, ...]
