"""Keyword selection rules for the deterministic v1 text analysis."""

from __future__ import annotations

from collections.abc import Iterable

from src.schemas import WordFrequency

STOPWORDS = frozenset(
    {
        "a",
        "al",
        "and",
        "de",
        "del",
        "el",
        "en",
        "es",
        "for",
        "in",
        "la",
        "las",
        "los",
        "of",
        "or",
        "para",
        "por",
        "the",
        "to",
        "un",
        "una",
        "y",
    }
)


def select_keywords(frequencies: Iterable[WordFrequency]) -> list[WordFrequency]:
    """Return at most five non-stopword frequencies in their existing stable order."""

    return [frequency for frequency in frequencies if frequency.word not in STOPWORDS][:5]
