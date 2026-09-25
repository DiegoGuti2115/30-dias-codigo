"""Conservative text normalization before character-based chunking."""

from __future__ import annotations

import re

_HORIZONTAL_WHITESPACE = re.compile(r"[^\S\r\n]+")
_EXCESSIVE_BLANK_LINES = re.compile(r"\n{3,}")


def normalize_text(text: str) -> str:
    """Normalize spacing while preserving paragraph boundaries and text order.

    Line endings become ``\n``, horizontal whitespace is reduced to one space,
    and multiple blank lines become a single paragraph separator. Leading and
    trailing whitespace does not become part of a fragment.
    """
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = _HORIZONTAL_WHITESPACE.sub(" ", normalized)
    normalized = "\n".join(line.strip() for line in normalized.split("\n"))
    normalized = _EXCESSIVE_BLANK_LINES.sub("\n\n", normalized)
    return normalized.strip()
