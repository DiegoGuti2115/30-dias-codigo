"""Tests for Phase 4 JSON presentation helpers."""

from __future__ import annotations

from keyword_retrieval.corpus import Document
from keyword_retrieval.presentation import PREVIEW_LENGTH, build_response
from keyword_retrieval.retrieval import RetrievalResult


def test_build_response_limits_results_and_serializes_explanations() -> None:
    documents = (
        Document(id="first", content="First matching document."),
        Document(id="second", content="Second matching document."),
    )
    results = (
        RetrievalResult("first", 2, ("first", "matching")),
        RetrievalResult("second", 1, ("matching",)),
    )

    response = build_response(
        query="FIRST matching",
        corpus_path="data/corpus.json",
        document_count=2,
        limit=1,
        output_format="json",
        documents=documents,
        results=results,
    )

    assert response["normalized_terms"] == ["first", "matching"]
    assert response["format"] == "json"
    assert response["match_count"] == 2
    assert response["result_count"] == 1
    assert response["results"] == [
        {
            "id": "first",
            "score": 2,
            "matched_terms": ["first", "matching"],
            "preview": "First matching document.",
        }
    ]


def test_build_response_keeps_a_valid_empty_result_set() -> None:
    response = build_response(
        query="nothing",
        corpus_path="data/corpus.json",
        document_count=1,
        limit=10,
        output_format="json",
        documents=(Document(id="one", content="Local content."),),
        results=(),
    )

    assert response["match_count"] == 0
    assert response["result_count"] == 0
    assert response["results"] == []


def test_build_response_bounds_and_normalizes_preview_whitespace() -> None:
    content = f"  {'word ' * 40}  "
    response = build_response(
        query="word",
        corpus_path="data/corpus.json",
        document_count=1,
        limit=1,
        output_format="json",
        documents=(Document(id="one", content=content),),
        results=(RetrievalResult("one", 1, ("word",)),),
    )

    preview = response["results"][0]["preview"]
    assert len(preview) == PREVIEW_LENGTH
    assert preview.endswith("…")
    assert "  " not in preview
