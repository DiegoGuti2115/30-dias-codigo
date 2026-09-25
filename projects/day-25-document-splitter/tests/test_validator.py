"""Tests for Phase 1 document input validation."""

from pathlib import Path

import pytest

from document_splitter.validators.document import (
    DocumentValidationError,
    MAX_DOCUMENT_SIZE_BYTES,
    validate_document,
)


def _write_document(tmp_path: Path, name: str, content: str = "contenido") -> Path:
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


@pytest.mark.parametrize("extension", [".txt", ".pdf", ".docx", ".TXT"])
def test_validate_document_accepts_supported_non_empty_files(
    tmp_path: Path, extension: str
) -> None:
    source = _write_document(tmp_path, f"documento{extension}")

    document = validate_document(source, chunk_size=1_000, overlap=150)

    assert document.path == source.resolve()
    assert document.extension == extension.lower()
    assert document.size_bytes == len("contenido".encode("utf-8"))


def test_validate_document_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(DocumentValidationError, match="no existe"):
        validate_document(tmp_path / "ausente.txt", chunk_size=100, overlap=10)


def test_validate_document_rejects_directory(tmp_path: Path) -> None:
    with pytest.raises(DocumentValidationError, match="no corresponde a un archivo"):
        validate_document(tmp_path, chunk_size=100, overlap=10)


def test_validate_document_rejects_unsupported_extension(tmp_path: Path) -> None:
    source = _write_document(tmp_path, "archivo.csv")

    with pytest.raises(DocumentValidationError, match="Formato no permitido"):
        validate_document(source, chunk_size=100, overlap=10)


def test_validate_document_rejects_empty_file(tmp_path: Path) -> None:
    source = _write_document(tmp_path, "vacio.txt", content="")

    with pytest.raises(DocumentValidationError, match="está vacío"):
        validate_document(source, chunk_size=100, overlap=10)


def test_validate_document_rejects_file_over_the_configured_limit(tmp_path: Path) -> None:
    source = _write_document(tmp_path, "grande.txt", content="12345")

    with pytest.raises(DocumentValidationError, match="supera el límite"):
        validate_document(source, chunk_size=100, overlap=10, max_size_bytes=4)


@pytest.mark.parametrize(
    ("chunk_size", "overlap", "message"),
    [
        (0, 0, "--chunk-size"),
        (-1, 0, "--chunk-size"),
        (100, -1, "--overlap no puede"),
        (100, 100, "menor que --chunk-size"),
        (100, 101, "menor que --chunk-size"),
    ],
)
def test_validate_document_rejects_invalid_chunking_arguments(
    tmp_path: Path, chunk_size: int, overlap: int, message: str
) -> None:
    source = _write_document(tmp_path, "documento.txt")

    with pytest.raises(DocumentValidationError, match=message):
        validate_document(source, chunk_size=chunk_size, overlap=overlap)


def test_document_size_limit_matches_the_documented_25_megabytes() -> None:
    assert MAX_DOCUMENT_SIZE_BYTES == 25 * 1024 * 1024
