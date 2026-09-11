"""Unit tests for the Phase 4 pure local inspection service."""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, cast

import pytest
from src.filename_validation import FilenameValidationError
from src.inspection import (
    READ_CHUNK_SIZE_BYTES,
    FileTooLargeError,
    inspect_file,
)
from src.schemas import MAX_FILE_SIZE_BYTES

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class RecordingStream(BytesIO):
    """In-memory stream that records requested read sizes for bounded-read tests."""

    def __init__(self, initial_bytes: bytes) -> None:
        super().__init__(initial_bytes)
        self.requested_sizes: list[int | None] = []

    def read(self, size: int | None = -1) -> bytes:
        self.requested_sizes.append(size)
        return super().read(size)


def test_inspect_file_returns_the_public_contract_for_known_content() -> None:
    content = b"Hello, inspector!\n"

    result = inspect_file(
        BytesIO(content),
        filename="report.PDF",
        media_type_declared="application/pdf",
    )

    assert result.model_dump() == {
        "filename": "report.PDF",
        "size_bytes": len(content),
        "media_type_declared": "application/pdf",
        "extension": "pdf",
        "filename_checks": {
            "is_safe": True,
            "has_path_separator": False,
            "has_traversal_sequence": False,
            "has_control_characters": False,
            "has_ambiguous_extension": False,
        },
        "content_fingerprint": {
            "algorithm": "sha256",
            "value": "1bf3aefc56ee29340feee1a39a2964489873a899f63796ebe71715d06368a941",
        },
    }


def test_inspect_file_matches_the_versioned_safe_fixture() -> None:
    fixture_path = PROJECT_ROOT / "data" / "fixtures" / "phase-4-sample.txt"
    expected_path = PROJECT_ROOT / "data" / "expected" / "phase-4-sample.json"

    result = inspect_file(
        BytesIO(fixture_path.read_bytes()),
        filename="phase-4-sample.txt",
        media_type_declared="text/plain",
    )

    assert result.model_dump() == json.loads(expected_path.read_text(encoding="utf-8"))


def test_inspect_file_accepts_empty_content_and_absent_declared_media_type() -> None:
    result = inspect_file(BytesIO(b""), filename="empty.txt")

    assert result.size_bytes == 0
    assert result.media_type_declared is None
    assert result.content_fingerprint.value == (
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )


def test_inspect_file_is_deterministic_and_marks_ambiguous_extensions() -> None:
    content = b"same bytes"

    first = inspect_file(
        BytesIO(content), filename="archive.tar.gz", media_type_declared="text/plain"
    )
    second = inspect_file(
        BytesIO(content), filename="archive.tar.gz", media_type_declared="text/plain"
    )

    assert first == second
    assert first.extension == "gz"
    assert first.filename_checks.has_ambiguous_extension is True


def test_inspect_file_reads_content_in_bounded_blocks() -> None:
    content = b"a" * (READ_CHUNK_SIZE_BYTES * 2 + 1)
    stream = RecordingStream(content)

    result = inspect_file(stream, filename="large.txt")

    assert result.size_bytes == len(content)
    assert stream.requested_sizes
    assert all(
        requested_size is not None and requested_size <= READ_CHUNK_SIZE_BYTES
        for requested_size in stream.requested_sizes
    )


def test_inspect_file_rejects_content_larger_than_the_public_limit() -> None:
    stream = RecordingStream(b"a" * (MAX_FILE_SIZE_BYTES + 1))

    with pytest.raises(FileTooLargeError):
        inspect_file(stream, filename="too-large.bin")

    assert all(
        requested_size is not None and requested_size <= READ_CHUNK_SIZE_BYTES
        for requested_size in stream.requested_sizes
    )


def test_inspect_file_rejects_invalid_filename_before_reading_content() -> None:
    stream = RecordingStream(b"content must not be consumed")

    with pytest.raises(FilenameValidationError):
        inspect_file(stream, filename="../unsafe.txt")

    assert stream.requested_sizes == []


def test_inspect_file_rejects_non_bytes_stream_data() -> None:
    class TextStream:
        def read(self, size: int) -> str:
            return "not bytes"

    with pytest.raises(TypeError, match="must return bytes"):
        inspect_file(cast(BinaryIO, TextStream()), filename="text.txt")


def test_inspect_file_rejects_invalid_declared_media_type_without_coercion() -> None:
    with pytest.raises(TypeError, match="media_type_declared"):
        inspect_file(BytesIO(b"content"), filename="file.txt", media_type_declared=123)
