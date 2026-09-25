"""Tests for ordered text extraction in Phase 2."""

from __future__ import annotations

from pathlib import Path

import pytest

from document_splitter.extractors.base import DocumentExtractionError
from document_splitter.extractors.registry import extract_document, get_extractor
from document_splitter.extractors.txt import TextExtractor

FIXTURES_DIRECTORY = Path(__file__).parent / "fixtures"


@pytest.mark.parametrize(
    ("name", "expected_fragments"),
    [
        ("sample.txt", ["Primera linea.", "Segunda linea en orden."]),
        ("sample.pdf", ["PDF primera pagina.", "PDF segunda pagina."]),
        ("sample.docx", ["DOCX primer parrafo.", "DOCX segundo parrafo."]),
    ],
)
def test_extract_document_returns_non_empty_text_in_source_order(
    name: str, expected_fragments: list[str]
) -> None:
    source = FIXTURES_DIRECTORY / name
    text = extract_document(source, source.suffix)
    assert text.strip()
    positions = [text.index(fragment) for fragment in expected_fragments]
    assert positions == sorted(positions)


def test_get_extractor_selects_the_supported_format_case_insensitively() -> None:
    assert isinstance(get_extractor(".TXT"), TextExtractor)


def test_get_extractor_rejects_an_unregistered_format() -> None:
    with pytest.raises(DocumentExtractionError, match="No hay extractor registrado"):
        get_extractor(".csv")


def test_text_extractor_rejects_non_utf8_content(tmp_path: Path) -> None:
    source = tmp_path / "invalid.txt"
    source.write_bytes(b"\xff\xfe")
    with pytest.raises(DocumentExtractionError, match="UTF-8"):
        TextExtractor().extract(source)


def test_text_extractor_rejects_whitespace_only_content(tmp_path: Path) -> None:
    source = tmp_path / "blank.txt"
    source.write_text(" \n\t", encoding="utf-8")
    with pytest.raises(DocumentExtractionError, match="no contiene texto extraíble"):
        TextExtractor().extract(source)


def test_pdf_extractor_rejects_a_non_pdf_file(tmp_path: Path) -> None:
    source = tmp_path / "invalid.pdf"
    source.write_text("esto no es un PDF", encoding="utf-8")
    with pytest.raises(DocumentExtractionError, match="No se pudo extraer texto"):
        extract_document(source, ".pdf")


def test_docx_extractor_rejects_a_non_docx_file(tmp_path: Path) -> None:
    source = tmp_path / "invalid.docx"
    source.write_text("esto no es un DOCX", encoding="utf-8")
    with pytest.raises(DocumentExtractionError, match="No se pudo leer el archivo DOCX"):
        extract_document(source, ".docx")
