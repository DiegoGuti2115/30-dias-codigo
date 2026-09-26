"""Unit tests for deterministic Phase 3 keyword retrieval."""

from __future__ import annotations

from keyword_retrieval.corpus import Document
from keyword_retrieval.retrieval import normalize_text, retrieve_documents, tokenize


def test_normalize_text_casefolds_and_removes_accents() -> None:
    assert normalize_text("ÁRBOL Café") == "arbol cafe"


def test_tokenize_splits_punctuation_and_ignores_repeated_whitespace() -> None:
    assert tokenize(" Azure,   AI-search! ") == ("azure", "ai", "search")


def test_retrieve_documents_uses_exact_normalized_word_matches() -> None:
    documents = (
        Document(id="accented", content="El café usa Azure."),
        Document(id="partial", content="Cafeteria and azures are different words."),
        Document(id="none", content="Unrelated document."),
    )

    results = retrieve_documents("CAFÉ azure", documents)

    assert [(result.document_id, result.score, result.matched_terms) for result in results] == [
        ("accented", 2, ("cafe", "azure")),
    ]


def test_retrieve_documents_counts_each_distinct_query_term_once() -> None:
    documents = (
        Document(id="both", content="Keyword keyword retrieval retrieval."),
        Document(id="one", content="Keyword only."),
    )

    results = retrieve_documents("keyword KEYWORD retrieval", documents)

    assert [(result.document_id, result.score, result.matched_terms) for result in results] == [
        ("both", 2, ("keyword", "retrieval")),
        ("one", 1, ("keyword",)),
    ]


def test_retrieve_documents_orders_ties_by_document_id() -> None:
    documents = (
        Document(id="zeta", content="local match"),
        Document(id="alpha", content="local match"),
        Document(id="middle", content="local other"),
    )

    results = retrieve_documents("local match", documents)

    assert [result.document_id for result in results] == ["alpha", "zeta", "middle"]
    assert [result.score for result in results] == [2, 2, 1]


def test_retrieve_documents_returns_no_results_when_no_terms_match() -> None:
    documents = (Document(id="one", content="Local keyword retrieval."),)

    assert retrieve_documents("cloud", documents) == ()
