"""Character-based text chunking with readable boundary preferences."""

from __future__ import annotations

from dataclasses import dataclass
import re

from document_splitter.processors.normalizer import normalize_text

_SENTENCE_BOUNDARY = re.compile(r"[.!?](?:[\"'»”)]*)\s+")


@dataclass(frozen=True)
class TextChunk:
    """An ordered text fragment and its range in normalized source text."""

    index: int
    text: str
    start_char: int
    end_char: int


def split_text(text: str, *, chunk_size: int, overlap: int) -> list[TextChunk]:
    """Normalize and divide text by preferred boundaries with character overlap.

    The splitter prefers paragraph, sentence, then whitespace boundaries. A word
    longer than ``chunk_size`` remains intact, which is the only permitted case
    where a chunk can exceed the configured limit.
    """
    _validate_chunking_arguments(chunk_size=chunk_size, overlap=overlap)
    normalized = normalize_text(text)
    if not normalized:
        return []

    chunks: list[TextChunk] = []
    start = 0
    length = len(normalized)

    while start < length:
        end = _select_end(normalized, start=start, chunk_size=chunk_size)
        chunk_text = normalized[start:end].strip()
        if not chunk_text:
            break

        chunks.append(
            TextChunk(
                index=len(chunks),
                text=chunk_text,
                start_char=start,
                end_char=start + len(chunk_text),
            )
        )
        if end >= length:
            break

        next_start = max(end - overlap, start + 1)
        while next_start < length and normalized[next_start].isspace():
            next_start += 1
        start = next_start

    return chunks


def _select_end(text: str, *, start: int, chunk_size: int) -> int:
    """Find the best chunk endpoint, preserving an oversized indivisible word."""
    limit = min(start + chunk_size, len(text))
    if limit == len(text):
        return limit

    if text[limit].isspace():
        return limit

    segment = text[start:limit]
    paragraph_end = segment.rfind("\n\n")
    if paragraph_end > 0:
        return start + paragraph_end

    sentence_ends = [match.end() for match in _SENTENCE_BOUNDARY.finditer(segment)]
    if sentence_ends:
        return start + sentence_ends[-1]

    space_end = max(segment.rfind(" "), segment.rfind("\n"))
    if space_end > 0:
        return start + space_end

    next_space = re.search(r"\s", text[limit:])
    if next_space is not None:
        return limit + next_space.start()
    return len(text)


def _validate_chunking_arguments(*, chunk_size: int, overlap: int) -> None:
    """Protect direct callers that do not pass through CLI validation."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")
    if overlap < 0:
        raise ValueError("overlap cannot be negative")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")
