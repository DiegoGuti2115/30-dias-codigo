"""PDF text extraction backed by PyMuPDF."""

from __future__ import annotations

from pathlib import Path

from document_splitter.extractors.base import ExtractedDocument, DocumentExtractionError


class PdfExtractor:
    """Extract selectable text page by page from a PDF document."""

    def extract(self, source: Path) -> ExtractedDocument:
        """Return PDF text in page order, rejecting encrypted or image-only PDFs."""
        try:
            import pymupdf
        except ImportError as error:
            raise DocumentExtractionError(
                "La extracción PDF requiere instalar PyMuPDF."
            ) from error

        try:
            with pymupdf.open(source) as document:
                if document.needs_pass:
                    raise DocumentExtractionError(
                        f"El PDF está protegido con contraseña: {source}"
                    )
                text = "\n".join(page.get_text("text") for page in document)
        except DocumentExtractionError:
            raise
        except (pymupdf.FileDataError, OSError, RuntimeError) as error:
            raise DocumentExtractionError(
                f"No se pudo extraer texto del PDF: {source}"
            ) from error

        if not text.strip():
            raise DocumentExtractionError(
                f"El PDF no contiene texto extraíble; OCR no está incluido: {source}"
            )

        return ExtractedDocument(source=source, text=text)
