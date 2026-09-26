"""Unit tests for the Phase 2 local corpus contract."""

from __future__ import annotations

import json

import pytest

from keyword_retrieval.corpus import load_corpus, validate_corpus, validate_request
from keyword_retrieval.errors import ValidationError


def test_load_corpus_returns_validated_documents(tmp_path) -> None:
    corpus = tmp_path / "corpus.json"
    corpus.write_text(
        json.dumps(
            [
                {"id": "second", "content": "Second document."},
                {"id": "first", "content": "First document."},
            ]
        ),
        encoding="utf-8",
    )

    documents = load_corpus(corpus)

    assert [(document.id, document.content) for document in documents] == [
        ("second", "Second document."),
        ("first", "First document."),
    ]


@pytest.mark.parametrize(
    ("payload", "code"),
    [
        ([], "empty_corpus"),
        ({"id": "one", "content": "Text"}, "invalid_corpus_schema"),
        (["not-a-document"], "invalid_document"),
        ([{"content": "Missing id"}], "invalid_document_id"),
        ([{"id": "one", "content": "  "}], "invalid_document_content"),
        (
            [
                {"id": "duplicate", "content": "First"},
                {"id": "duplicate", "content": "Second"},
            ],
            "duplicate_document_id",
        ),
    ],
)
def test_validate_corpus_rejects_invalid_document_contracts(payload, code) -> None:
    with pytest.raises(ValidationError) as error:
        validate_corpus(payload)

    assert error.value.code == code


@pytest.mark.parametrize(
    ("name", "content", "code"),
    [
        ("corpus.txt", "[]", "invalid_corpus_extension"),
        ("corpus.json", "{", "invalid_corpus_json"),
    ],
)
def test_load_corpus_rejects_invalid_files(tmp_path, name, content, code) -> None:
    corpus = tmp_path / name
    corpus.write_text(content, encoding="utf-8")

    with pytest.raises(ValidationError) as error:
        load_corpus(corpus)

    assert error.value.code == code


def test_load_corpus_rejects_a_directory(tmp_path) -> None:
    with pytest.raises(ValidationError) as error:
        load_corpus(tmp_path)

    assert error.value.code == "invalid_corpus_path"


@pytest.mark.parametrize(
    ("query", "limit", "code"),
    [("", 1, "invalid_query"), ("query", 0, "invalid_limit")],
)
def test_validate_request_rejects_invalid_values(query, limit, code) -> None:
    with pytest.raises(ValidationError) as error:
        validate_request(query, limit)

    assert error.value.code == code
