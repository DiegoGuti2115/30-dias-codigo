"""Generación determinista de anclas e índices para el contrato Markdown v1."""

from __future__ import annotations

from dataclasses import dataclass
import unicodedata
from collections.abc import Iterable

from parser import Heading


@dataclass(frozen=True)
class TocEntry:
    """Encabezado enriquecido con ancla y profundidad de presentación."""

    line: int
    level: int
    text: str
    anchor: str
    depth: int


def normalize_anchor(text: str) -> str:
    """Return the unsuffixed v1 anchor base for a visible heading label."""

    normalized = unicodedata.normalize("NFKD", text)
    retained: list[str] = []
    for character in normalized:
        if unicodedata.category(character).startswith("M"):
            continue
        lowered = character.lower()
        if lowered.isalnum() or lowered in {"-", " ", "\t"}:
            retained.append(lowered)

    joined = "".join(retained)
    collapsed = "-".join(part for part in joined.replace("\t", " ").replace("-", " ").split() if part)
    return collapsed or "seccion"


def build_entries(headings: Iterable[Heading]) -> tuple[TocEntry, ...]:
    """Assign unique anchors and contract-defined presentation depths in order."""

    entries: list[TocEntry] = []
    occurrences: dict[str, int] = {}
    level_stack: list[tuple[int, int]] = []
    previous_level: int | None = None
    current_depth = 0

    for heading in headings:
        base = normalize_anchor(heading.text)
        occurrences[base] = occurrences.get(base, 0) + 1
        ordinal = occurrences[base]
        anchor = base if ordinal == 1 else f"{base}-{ordinal}"

        if previous_level is None:
            current_depth = 0
            level_stack = [(heading.level, current_depth)]
        elif heading.level > previous_level:
            current_depth += 1
            level_stack.append((heading.level, current_depth))
        elif heading.level == previous_level:
            pass
        else:
            matching = next(
                ((level, depth) for level, depth in reversed(level_stack) if level <= heading.level),
                None,
            )
            if matching is None:
                current_depth = 0
                level_stack = [(heading.level, current_depth)]
            else:
                _, current_depth = matching
                level_stack = [(level, depth) for level, depth in level_stack if depth <= current_depth]
                if not level_stack or level_stack[-1][0] != heading.level:
                    level_stack.append((heading.level, current_depth))

        entries.append(
            TocEntry(
                line=heading.line,
                level=heading.level,
                text=heading.text,
                anchor=anchor,
                depth=current_depth,
            )
        )
        previous_level = heading.level

    return tuple(entries)


def render_toc(entries: Iterable[TocEntry]) -> str:
    """Render a stable, unordered Markdown list using two spaces per depth."""

    return "\n".join(
        f"{'  ' * entry.depth}- [{entry.text}](#{entry.anchor})" for entry in entries
    )
