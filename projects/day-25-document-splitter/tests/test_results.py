"""Tests for Phase 4 traceable JSON result generation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from document_splitter.chunkers.text import split_text
from document_splitter.services.results import build_document_result
from document_splitter.utils.files import (
    ResultWritingError,
    default_output_path,
    serialize_result,
    write_result,
)
from document_splitter.utils.hashing import calculate_document_id


def test_calculate_document_id_uses_the_source_bytes_deterministically(tmp_path: Path) -> None:
    source = tmp_path / "documento.txt"
    source.write_bytes(b"contenido\r\n")

    expected_digest = hashlib.sha256(b"contenido\r\n").hexdigest()
    assert calculate_document_id(source) == f"sha256:{expected_digest}"
    assert calculate_document_id(source) == f"sha256:{expected_digest}"


def test_result_serialization_preserves_chunk_indices_ranges_and_configuration(
    tmp_path: Path,
) -> None:
    source = tmp_path / "notas.txt"
    source.write_text("uno dos tres cuatro", encoding="utf-8")
    chunks = split_text(source.read_text(encoding="utf-8"), chunk_size=10, overlap=3)
    document_id = calculate_document_id(source)

    result = build_document_result(
        source=source,
        document_id=document_id,
        chunk_size=10,
        overlap=3,
        chunks=chunks,
    )
    payload = json.loads(serialize_result(result))

    assert payload["source"] == "notas.txt"
    assert payload["document_id"] == document_id
    assert payload["chunk_size"] == 10
    assert payload["overlap"] == 3
    assert [chunk["index"] for chunk in payload["chunks"]] == list(range(len(chunks)))
    assert [chunk["text"] for chunk in payload["chunks"]] == [chunk.text for chunk in chunks]
    assert [chunk["start_char"] for chunk in payload["chunks"]] == [
        chunk.start_char for chunk in chunks
    ]
    assert [chunk["end_char"] for chunk in payload["chunks"]] == [
        chunk.end_char for chunk in chunks
    ]
    assert [chunk["id"] for chunk in payload["chunks"]] == [
        f"{document_id}-{chunk.index}" for chunk in chunks
    ]


def test_write_result_creates_readable_json_without_replacing_a_conflict(tmp_path: Path) -> None:
    source = tmp_path / "notas.txt"
    source.write_text("contenido", encoding="utf-8")
    result = build_document_result(
        source=source,
        document_id=calculate_document_id(source),
        chunk_size=100,
        overlap=0,
        chunks=split_text("contenido", chunk_size=100, overlap=0),
    )
    destination = tmp_path / "nested" / "notas.json"

    assert write_result(result, destination) == destination.resolve()
    assert json.loads(destination.read_text(encoding="utf-8"))["chunks"][0]["text"] == "contenido"
    with pytest.raises(ResultWritingError, match="ya existe"):
        write_result(result, destination)


def test_default_output_path_is_stable_and_uses_the_source_stem() -> None:
    assert default_output_path(Path("entrada/manual.v1.txt")) == Path("output/manual.v1.json")
