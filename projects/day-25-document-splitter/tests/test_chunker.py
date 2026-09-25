"""Tests for Phase 3 text normalization and chunking."""

from __future__ import annotations

import pytest

from document_splitter.chunkers.text import split_text
from document_splitter.processors.normalizer import normalize_text


def test_normalize_text_preserves_paragraphs_and_unicode_order() -> None:
    text = "  Árbol\t azul\r\n\r\n\r\n  niño   \rsegunda línea  "
    assert normalize_text(text) == "Árbol azul\n\nniño\nsegunda línea"


def test_split_text_prefers_paragraph_boundaries() -> None:
    chunks = split_text("Primer párrafo breve.\n\nSegundo párrafo breve.", chunk_size=24, overlap=0)
    assert [chunk.text for chunk in chunks] == [
        "Primer párrafo breve.",
        "Segundo párrafo breve.",
    ]
    assert [chunk.index for chunk in chunks] == [0, 1]
    assert [(chunk.start_char, chunk.end_char) for chunk in chunks] == [(0, 21), (23, 45)]


def test_split_text_prefers_sentence_then_space_boundaries() -> None:
    chunks = split_text(
        "Primera frase corta. Segunda frase también corta.",
        chunk_size=25,
        overlap=0,
    )
    assert [chunk.text for chunk in chunks] == [
        "Primera frase corta.",
        "Segunda frase también",
        "corta.",
    ]


def test_split_text_applies_overlap_between_chunks() -> None:
    chunks = split_text("uno dos tres cuatro cinco", chunk_size=10, overlap=3)
    assert [chunk.text for chunk in chunks] == [
        "uno dos",
        "dos tres",
        "res cuatro",
        "tro cinco",
    ]
    for previous, current in zip(chunks, chunks[1:]):
        assert previous.text[-3:] == current.text[:3]


def test_split_text_keeps_an_indivisible_word_larger_than_limit() -> None:
    chunks = split_text("supercalifragilistico breve", chunk_size=10, overlap=0)
    assert [chunk.text for chunk in chunks] == ["supercalifragilistico", "breve"]
    assert len(chunks[0].text) > 10


def test_split_text_returns_no_chunks_for_whitespace_only_text() -> None:
    assert split_text(" \r\n\t ", chunk_size=10, overlap=0) == []


@pytest.mark.parametrize(
    ("chunk_size", "overlap"),
    [(0, 0), (-1, 0), (10, -1), (10, 10)],
)
def test_split_text_rejects_invalid_direct_configuration(
    chunk_size: int, overlap: int
) -> None:
    with pytest.raises(ValueError):
        split_text("contenido", chunk_size=chunk_size, overlap=overlap)


def test_split_text_respects_limit_for_breakable_content() -> None:
    chunks = split_text("uno dos tres cuatro cinco seis", chunk_size=10, overlap=2)
    assert all(len(chunk.text) <= 10 for chunk in chunks)
    assert [chunk.index for chunk in chunks] == list(range(len(chunks)))
    assert all(chunk.end_char - chunk.start_char == len(chunk.text) for chunk in chunks)
    assert [chunk.start_char for chunk in chunks] == sorted(chunk.start_char for chunk in chunks)
