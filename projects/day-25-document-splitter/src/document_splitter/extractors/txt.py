"""UTF-8 text document extraction."""

from __future__ import annotations

from pathlib import Path

from document_splitter.extractors.base import ExtractedDocument, DocumentExtractionError


class TextExtractor:
    """Extract text from UTF-8 encoded plain-text files."""

    def extract(self, source: Path) -> ExtractedDocument:
        """Return the source text without changing its order or whitespace."""
        try:
            text = source.read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            raise DocumentExtractionError(
                f"El archivo TXT debe estar codificado en UTF-8: {source}"
            ) from error
        except OSError as error:
            raise DocumentExtractionError(
                f"No se pudo leer el archivo TXT: {source}"
            ) from error

        if not text.strip():
            raise DocumentExtractionError(
                f"El archivo TXT no contiene texto extraíble: {source}"
            )

        return ExtractedDocument(source=source, text=text)
