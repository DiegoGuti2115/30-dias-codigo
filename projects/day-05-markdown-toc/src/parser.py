"""Interpretación sin efectos laterales de la gramática Markdown v1."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable

_ATX_HEADING = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.*)$")
_FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})")


@dataclass(frozen=True)
class Heading:
    """Encabezado ATX elegible conservando su posición física."""

    line: int
    level: int
    text: str


@dataclass(frozen=True)
class ParseResult:
    """Resultado inmutable de interpretar un documento sin modificarlo."""

    headings: tuple[Heading, ...]
    excluded_from_line: int | None = None


def parse_markdown(document: str) -> ParseResult:
    """Extract eligible ATX headings from *document* according to contract v1.

    The function is deliberately text-only: it never reads, writes, or validates a
    path. An unclosed fenced-code block excludes every remaining physical line.
    """

    headings: list[Heading] = []
    fence_character: str | None = None
    fence_length = 0
    excluded_from_line: int | None = None

    for line_number, raw_line in enumerate(document.splitlines(), start=1):
        line = raw_line.rstrip("\r\n")

        if fence_character is not None:
            if _closes_fence(line, fence_character, fence_length):
                fence_character = None
                fence_length = 0
            continue

        opening_fence = _opening_fence(line)
        if opening_fence is not None:
            fence_character, fence_length = opening_fence
            excluded_from_line = line_number
            continue

        heading = _parse_atx_heading(line, line_number)
        if heading is not None:
            headings.append(heading)

    return ParseResult(tuple(headings), excluded_from_line if fence_character is not None else None)


def parse_lines(lines: Iterable[str]) -> ParseResult:
    """Parse an iterable of lines while preserving the same line-number semantics."""

    return parse_markdown("".join(lines))


def _parse_atx_heading(line: str, line_number: int) -> Heading | None:
    match = _ATX_HEADING.match(line)
    if match is None:
        return None

    text = match.group(2).strip(" \t")
    text = re.sub(r"[ \t]+#+[ \t]*$", "", text).strip(" \t")
    if not text:
        return None

    return Heading(line=line_number, level=len(match.group(1)), text=text)


def _opening_fence(line: str) -> tuple[str, int] | None:
    match = _FENCE_OPEN.match(line)
    if match is None:
        return None
    delimiter = match.group(1)
    return delimiter[0], len(delimiter)


def _closes_fence(line: str, character: str, minimum_length: int) -> bool:
    match = re.match(rf"^ {{0,3}}({re.escape(character)}+)[ \t]*$", line)
    return match is not None and len(match.group(1)) >= minimum_length
