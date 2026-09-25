"""Build stable, traceable document-splitting results."""

from __future__ import annotations

from pathlib import Path

from document_splitter.chunkers.text import TextChunk
from document_splitter.models import DocumentResult, ResultChunk


def build_document_result(
    *,
    source: Path,
    document_id: str,
    chunk_size: int,
    overlap: int,
    chunks: list[TextChunk],
) -> DocumentResult:
    """Build a deterministic result preserving chunk order, text, and ranges."""
    return DocumentResult(
        source=source.name,
        document_id=document_id,
        chunk_size=chunk_size,
        overlap=overlap,
        chunks=tuple(
            ResultChunk(
                id=f"{document_id}-{chunk.index}",
                index=chunk.index,
                text=chunk.text,
                start_char=chunk.start_char,
                end_char=chunk.end_char,
            )
            for chunk in chunks
        ),
    )
