"""Deterministic file identity helpers."""

from __future__ import annotations

import hashlib
from pathlib import Path

_HASH_BLOCK_SIZE = 64 * 1024


def calculate_document_id(source: Path) -> str:
    """Return the SHA-256 identity of the exact bytes stored in ``source``."""
    digest = hashlib.sha256()
    try:
        with source.open("rb") as file:
            for block in iter(lambda: file.read(_HASH_BLOCK_SIZE), b""):
                digest.update(block)
    except OSError as error:
        raise DocumentHashingError(f"No se pudo calcular el hash del archivo: {source}") from error
    return f"sha256:{digest.hexdigest()}"


class DocumentHashingError(RuntimeError):
    """Raised when a validated source cannot be read to calculate its hash."""
