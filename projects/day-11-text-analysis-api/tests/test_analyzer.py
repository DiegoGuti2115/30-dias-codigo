"""Unit tests for the pure Phase 4 text-analysis core."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from src.analyzer import analyze_text
from src.tokenizer import normalized_words, paragraph_count, sentence_count

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_analyze_text_matches_the_versioned_contract_fixture() -> None:
    text = (PROJECT_ROOT / "data" / "fixtures" / "contract-example.txt").read_text(encoding="utf-8")
    expected = json.loads(
        (PROJECT_ROOT / "data" / "expected" / "contract-example.json").read_text(encoding="utf-8")
    )

    assert analyze_text(text).model_dump() == expected


def test_analyze_text_handles_whitespace_only_text() -> None:
    result = analyze_text(" \t\n ")

    assert result.model_dump() == {
        "metrics": {
            "character_count": 4,
            "character_count_without_whitespace": 0,
            "word_count": 0,
            "sentence_count": 0,
            "paragraph_count": 0,
            "estimated_reading_time_seconds": 0,
        },
        "word_frequencies": [],
        "keywords": [],
    }


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Hola, MUNDO!", ["hola", "mundo"]),
        ("re-usable_test", ["re", "usable", "test"]),
        ("C# y 2026", ["c", "y", "2026"]),
        ("canción cancion", ["canción", "cancion"]),
        ("Cafe\u0301 CAFÉ", ["café", "café"]),
    ],
)
def test_normalized_words_follow_unicode_and_separator_rules(
    text: str, expected: list[str]
) -> None:
    assert normalized_words(text) == expected


def test_analyze_text_orders_frequency_ties_and_excludes_stopwords_from_keywords() -> None:
    result = analyze_text("La beta, alpha! beta y alpha; gamma de gamma.")

    assert [frequency.model_dump() for frequency in result.word_frequencies] == [
        {"word": "alpha", "count": 2},
        {"word": "beta", "count": 2},
        {"word": "gamma", "count": 2},
        {"word": "de", "count": 1},
        {"word": "la", "count": 1},
        {"word": "y", "count": 1},
    ]
    assert [frequency.model_dump() for frequency in result.keywords] == [
        {"word": "alpha", "count": 2},
        {"word": "beta", "count": 2},
        {"word": "gamma", "count": 2},
    ]


def test_analyze_text_limits_keywords_to_five() -> None:
    result = analyze_text("uno dos tres cuatro cinco seis siete")

    assert [frequency.word for frequency in result.keywords] == [
        "cinco",
        "cuatro",
        "dos",
        "seis",
        "siete",
    ]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Uno...?! Dos\nTres", 3),
        (" . ! … \n ", 0),
        ("Sin delimitador final", 1),
        ("Uno\r\nDos", 2),
    ],
)
def test_sentence_count_follows_delimiters_and_requires_words(text: str, expected: int) -> None:
    assert sentence_count(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Uno\nDos\n\nTres\n \t\nCuatro", 3),
        ("\n \t\n", 0),
        ("Uno\nDos", 1),
        ("...\n\n!?", 0),
    ],
)
def test_paragraph_count_uses_blank_line_groups_and_requires_words(
    text: str, expected: int
) -> None:
    assert paragraph_count(text) == expected


def test_reading_time_rounds_up_at_the_contract_speed() -> None:
    result = analyze_text("word " * 201)

    assert result.metrics.word_count == 201
    assert result.metrics.estimated_reading_time_seconds == 61


def test_analysis_is_deterministic_and_has_no_shared_state() -> None:
    first = analyze_text("Uno uno dos")
    second = analyze_text("tres")
    repeated_first = analyze_text("Uno uno dos")

    assert first.model_dump() == repeated_first.model_dump()
    assert [frequency.word for frequency in second.word_frequencies] == ["tres"]
