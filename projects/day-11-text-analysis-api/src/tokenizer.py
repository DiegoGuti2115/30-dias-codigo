"""Pure, deterministic text segmentation helpers for the v1 contract."""

from __future__ import annotations

import unicodedata

SENTENCE_DELIMITERS = frozenset({".", "!", "?", "…", "\n", "\r"})


def normalized_words(text: str) -> list[str]:
    """Return NFC-normalized, lowercase Unicode letter-or-digit tokens."""

    normalized_text = unicodedata.normalize("NFC", text).lower()
    words: list[str] = []
    current: list[str] = []

    for character in normalized_text:
        if character.isalpha() or character.isdigit():
            current.append(character)
        elif current:
            words.append("".join(current))
            current.clear()

    if current:
        words.append("".join(current))

    return words


def sentence_count(text: str) -> int:
    """Count non-empty word segments separated by contract sentence delimiters."""

    count = 0
    segment: list[str] = []

    for character in text:
        if character in SENTENCE_DELIMITERS:
            if normalized_words("".join(segment)):
                count += 1
            segment.clear()
        else:
            segment.append(character)

    if normalized_words("".join(segment)):
        count += 1

    return count


def paragraph_count(text: str) -> int:
    """Count non-empty groups of non-blank lines that contain at least one word."""

    count = 0
    paragraph_lines: list[str] = []

    for line in text.splitlines():
        if line.isspace() or not line:
            if normalized_words("\n".join(paragraph_lines)):
                count += 1
            paragraph_lines.clear()
        else:
            paragraph_lines.append(line)

    if normalized_words("\n".join(paragraph_lines)):
        count += 1

    return count
