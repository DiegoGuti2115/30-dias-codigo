"""Selection of a document extractor from a validated extension."""

from __future__ import annotations

from pathlib import Path

from document_splitter.extractors.base import DocumentExtractionError, DocumentExtractor
from document_splitter.extractors.docx import DocxExtractor
from document_splitter.extractors.pdf import PdfExtractor
from document_splitter.extractors.txt import TextExtractor

_EXTRACTORS: dict[str, DocumentExtractor] = {
    ".txt": TextExtractor(),
    ".pdf": PdfExtractor(),
    ".docx": DocxExtractor(),
}


def get_extractor(extension: str) -> DocumentExtractor:
    """Return the extractor registered for a validated filename extension."""
    try:
        return _EXTRACTORS[extension.lower()]
    except KeyError as error:
        raise DocumentExtractionError(
            f"No hay extractor registrado para el formato: {extension or '(sin extensión)'}"
        ) from error


def extract_document(source: Path, extension: str) -> str:
    """Extract text from ``source`` using the registered format adapter."""
    return get_extractor(extension).extract(source).text
