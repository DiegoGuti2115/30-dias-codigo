"""Input validation for the document processing command."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ALLOWED_EXTENSIONS = frozenset({".txt", ".pdf", ".docx"})
MAX_DOCUMENT_SIZE_BYTES = 25 * 1024 * 1024


class DocumentValidationError(ValueError):
    """Raised when a document path or chunking configuration is invalid."""


@dataclass(frozen=True)
class ValidatedDocument:
    """Validated metadata required by later processing phases."""

    path: Path
    extension: str
    size_bytes: int


def validate_document(
    source: Path,
    *,
    chunk_size: int,
    overlap: int,
    max_size_bytes: int = MAX_DOCUMENT_SIZE_BYTES,
) -> ValidatedDocument:
    """Validate a local document and chunking arguments without reading its content."""
    _validate_chunking_arguments(chunk_size=chunk_size, overlap=overlap)

    path = source.expanduser()
    if not path.exists():
        raise DocumentValidationError(f"El archivo no existe: {source}")
    if not path.is_file():
        raise DocumentValidationError(f"La ruta no corresponde a un archivo: {source}")

    extension = path.suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise DocumentValidationError(
            f"Formato no permitido: {extension or '(sin extensión)'}. "
            f"Formatos admitidos: {allowed}."
        )

    size_bytes = path.stat().st_size
    if size_bytes == 0:
        raise DocumentValidationError(f"El archivo está vacío: {source}")
    if size_bytes > max_size_bytes:
        raise DocumentValidationError(
            f"El archivo supera el límite de {max_size_bytes} bytes: {source}"
        )

    return ValidatedDocument(
        path=path.resolve(),
        extension=extension,
        size_bytes=size_bytes,
    )


def _validate_chunking_arguments(*, chunk_size: int, overlap: int) -> None:
    """Ensure the future fragmenting configuration is internally consistent."""
    if chunk_size <= 0:
        raise DocumentValidationError("--chunk-size debe ser un entero mayor que cero.")
    if overlap < 0:
        raise DocumentValidationError("--overlap no puede ser negativo.")
    if overlap >= chunk_size:
        raise DocumentValidationError("--overlap debe ser menor que --chunk-size.")
