"""Pure orchestration for deterministic text analysis defined by contract v1."""

from __future__ import annotations

from collections import Counter
from math import ceil

from src.keywords import select_keywords
from src.schemas import AnalyzeResponse, Metrics, WordFrequency
from src.tokenizer import normalized_words, paragraph_count, sentence_count

WORDS_PER_MINUTE = 200
SECONDS_PER_MINUTE = 60


def analyze_text(text: str) -> AnalyzeResponse:
    """Analyze text without side effects and return the contract response model."""

    words = normalized_words(text)
    frequencies = _sorted_frequencies(words)
    word_count = len(words)

    return AnalyzeResponse(
        metrics=Metrics(
            character_count=len(text),
            character_count_without_whitespace=sum(
                1 for character in text if not character.isspace()
            ),
            word_count=word_count,
            sentence_count=sentence_count(text),
            paragraph_count=paragraph_count(text),
            estimated_reading_time_seconds=_reading_time_seconds(word_count),
        ),
        word_frequencies=frequencies,
        keywords=select_keywords(frequencies),
    )


def _sorted_frequencies(words: list[str]) -> list[WordFrequency]:
    """Build frequency objects ordered by count descending and word ascending."""

    counts = Counter(words)
    return [
        WordFrequency(word=word, count=count)
        for word, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]


def _reading_time_seconds(word_count: int) -> int:
    """Estimate reading time at the contract's fixed speed of 200 words per minute."""

    return ceil(word_count / WORDS_PER_MINUTE * SECONDS_PER_MINUTE) if word_count else 0
