"""Pure, bounded local inspection of uploaded file content.

This module receives an already-open binary stream and untrusted metadata. It
never opens client-provided paths, persists bytes, calls the network, or emits
logs. HTTP request parsing and public error translation belong to Phase 5.
"""

from __future__ import annotations

from hashlib import sha256
from typing import BinaryIO

from src.filename_validation import validate_filename
from src.schemas import (
    MAX_FILE_SIZE_BYTES,
    ContentFingerprint,
    FilenameChecks,
    InspectionResponse,
)

READ_CHUNK_SIZE_BYTES = 64 * 1024


class FileTooLargeError(ValueError):
    """Raised when a content stream exceeds the public 5 MiB limit."""


def inspect_file(
    content: BinaryIO,
    *,
    filename: object,
    media_type_declared: object = None,
) -> InspectionResponse:
    """Inspect one binary stream according to the public v1 contract.

    The content is traversed in bounded blocks to calculate its exact byte size
    and SHA-256 fingerprint. No bytes are retained after each digest update.
    The caller owns the stream lifecycle and may map validation exceptions to an
    HTTP response in a later transport phase.
    """

    if not isinstance(media_type_declared, str | type(None)):
        raise TypeError("media_type_declared must be a string or None")

    assessment = validate_filename(filename)
    size_bytes, fingerprint = _measure_and_fingerprint(content)

    return InspectionResponse(
        filename=assessment.filename,
        size_bytes=size_bytes,
        media_type_declared=media_type_declared,
        extension=assessment.extension,
        filename_checks=FilenameChecks(
            is_safe=assessment.is_safe,
            has_path_separator=assessment.has_path_separator,
            has_traversal_sequence=assessment.has_traversal_sequence,
            has_control_characters=assessment.has_control_characters,
            has_ambiguous_extension=assessment.has_ambiguous_extension,
        ),
        content_fingerprint=ContentFingerprint(algorithm="sha256", value=fingerprint),
    )


def _measure_and_fingerprint(content: BinaryIO) -> tuple[int, str]:
    """Read a stream in bounded chunks and reject content past the size limit."""

    digest = sha256()
    size_bytes = 0

    while True:
        remaining_with_sentinel = MAX_FILE_SIZE_BYTES - size_bytes + 1
        chunk = content.read(min(READ_CHUNK_SIZE_BYTES, remaining_with_sentinel))
        if not chunk:
            return size_bytes, digest.hexdigest()
        if not isinstance(chunk, bytes):
            raise TypeError("content stream must return bytes")

        size_bytes += len(chunk)
        if size_bytes > MAX_FILE_SIZE_BYTES:
            raise FileTooLargeError("content exceeds the v1 size limit")
        digest.update(chunk)
