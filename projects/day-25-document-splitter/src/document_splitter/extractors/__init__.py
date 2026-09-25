"""Format-specific text extraction adapters."""

from document_splitter.extractors.base import (
    DocumentExtractionError,
    ExtractedDocument,
)
from document_splitter.extractors.registry import extract_document, get_extractor

__all__ = [
    "DocumentExtractionError",
    "ExtractedDocument",
    "extract_document",
    "get_extractor",
]
