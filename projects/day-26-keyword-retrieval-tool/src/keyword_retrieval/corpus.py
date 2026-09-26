"""Local JSON corpus loading and validation for Phase 2."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from keyword_retrieval.errors import ValidationError


@dataclass(frozen=True)
class Document:
    """A validated corpus document reserved for later retrieval phases."""

    id: str
    content: str


def validate_request(query: str, limit: int) -> None:
    """Validate request values that do not require reading the corpus."""
    if not query.strip():
        raise ValidationError("invalid_query", "query must contain non-whitespace text")
    if limit < 1:
        raise ValidationError("invalid_limit", "limit must be greater than zero")


def load_corpus(path: Path) -> tuple[Document, ...]:
    """Load and validate a JSON list of documents from a local file."""
    if not path.exists():
        raise ValidationError("corpus_not_found", "corpus file was not found")
    if not path.is_file():
        raise ValidationError("invalid_corpus_path", "corpus path must reference a file")
    if path.suffix.lower() != ".json":
        raise ValidationError("invalid_corpus_extension", "corpus must use the .json extension")

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError as error:
        raise ValidationError("invalid_corpus_encoding", "corpus must be UTF-8 text") from error
    except json.JSONDecodeError as error:
        raise ValidationError("invalid_corpus_json", "corpus must contain valid JSON") from error
    except OSError as error:
        raise ValidationError("unreadable_corpus", "corpus file could not be read") from error

    return validate_corpus(payload)


def validate_corpus(payload: Any) -> tuple[Document, ...]:
    """Validate the public corpus schema and return immutable documents."""
    if not isinstance(payload, list):
        raise ValidationError("invalid_corpus_schema", "corpus root must be a JSON array")
    if not payload:
        raise ValidationError("empty_corpus", "corpus must contain at least one document")

    documents: list[Document] = []
    seen_ids: set[str] = set()
    for index, raw_document in enumerate(payload):
        documents.append(_validate_document(raw_document, index, seen_ids))
    return tuple(documents)


def _validate_document(
    raw_document: Any, index: int, seen_ids: set[str]
) -> Document:
    if not isinstance(raw_document, dict):
        raise ValidationError(
            "invalid_document", f"document at index {index} must be a JSON object"
        )

    document_id = raw_document.get("id")
    content = raw_document.get("content")
    if not isinstance(document_id, str) or not document_id.strip():
        raise ValidationError(
            "invalid_document_id",
            f"document at index {index} must have a non-empty string id",
        )
    if document_id in seen_ids:
        raise ValidationError("duplicate_document_id", "document ids must be unique")
    if not isinstance(content, str) or not content.strip():
        raise ValidationError(
            "invalid_document_content",
            f"document '{document_id}' must have non-empty string content",
        )

    seen_ids.add(document_id)
    return Document(id=document_id, content=content)


