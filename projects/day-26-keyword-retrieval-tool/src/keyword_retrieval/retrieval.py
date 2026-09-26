"""Deterministic keyword normalization and local retrieval for Phase 3."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
import re
import unicodedata

from keyword_retrieval.corpus import Document

_TOKEN_PATTERN = re.compile(r"[^\W_]+", re.UNICODE)


@dataclass(frozen=True)
class RetrievalResult:
    """A local keyword match reserved for Phase 4 presentation."""

    document_id: str
    score: int
    matched_terms: tuple[str, ...]


def normalize_text(text: str) -> str:
    """Case-fold text and remove accent marks for deterministic comparison."""
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    return "".join(
        character
        for character in decomposed
        if not unicodedata.combining(character)
    )


def tokenize(text: str) -> tuple[str, ...]:
    """Return normalized word tokens, splitting on whitespace and punctuation."""
    return tuple(_TOKEN_PATTERN.findall(normalize_text(text)))


def retrieve_documents(
    query: str, documents: Iterable[Document]
) -> tuple[RetrievalResult, ...]:
    """Return exact word matches sorted by score descending and document ID."""
    query_terms = _unique_terms(tokenize(query))
    results: list[RetrievalResult] = []

    for document in documents:
        document_terms = set(tokenize(document.content))
        matched_terms = tuple(term for term in query_terms if term in document_terms)
        if matched_terms:
            results.append(
                RetrievalResult(
                    document_id=document.id,
                    score=len(matched_terms),
                    matched_terms=matched_terms,
                )
            )

    return tuple(sorted(results, key=lambda result: (-result.score, result.document_id)))


def _unique_terms(terms: Iterable[str]) -> tuple[str, ...]:
    """Keep the first occurrence of each normalized query term."""
    return tuple(dict.fromkeys(terms))
