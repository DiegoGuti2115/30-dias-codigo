"""JSON-ready presentation helpers for local and Azure AI Search CLI modes."""

from __future__ import annotations

from collections.abc import Iterable

from keyword_retrieval.azure_search import AzureSearchResult
from keyword_retrieval.corpus import Document
from keyword_retrieval.retrieval import RetrievalResult, tokenize

PREVIEW_LENGTH = 120


def build_response(
    *,
    query: str,
    corpus_path: str,
    document_count: int,
    limit: int,
    output_format: str,
    documents: Iterable[Document],
    results: Iterable[RetrievalResult],
) -> dict[str, object]:
    """Build the stable local response without performing retrieval itself."""
    document_by_id = {document.id: document for document in documents}
    all_results = tuple(results)
    limited_results = all_results[:limit]

    return {
        "phase": 5,
        "status": "completed",
        "source": "local",
        "query": query,
        "normalized_terms": list(dict.fromkeys(tokenize(query))),
        "corpus": corpus_path,
        "document_count": document_count,
        "limit": limit,
        "format": output_format,
        "match_count": len(all_results),
        "result_count": len(limited_results),
        "results": [
            _serialize_local_result(result, document_by_id[result.document_id])
            for result in limited_results
        ],
    }


def build_azure_response(
    *,
    query: str,
    index_name: str,
    limit: int,
    output_format: str,
    results: Iterable[AzureSearchResult],
) -> dict[str, object]:
    """Build the provider-distinct response from Azure AI Search results."""
    all_results = tuple(results)
    return {
        "phase": 5,
        "status": "completed",
        "source": "azure_ai_search",
        "query": query,
        "normalized_terms": list(dict.fromkeys(tokenize(query))),
        "index": index_name,
        "limit": limit,
        "format": output_format,
        "match_count": len(all_results),
        "result_count": len(all_results),
        "results": [
            {
                "id": result.document_id,
                "score": result.score,
                "preview": _preview(result.content),
            }
            for result in all_results
        ],
    }


def _serialize_local_result(result: RetrievalResult, document: Document) -> dict[str, object]:
    return {
        "id": result.document_id,
        "score": result.score,
        "matched_terms": list(result.matched_terms),
        "preview": _preview(document.content),
    }


def _preview(content: str) -> str:
    """Return a whitespace-normalized, bounded preview of document content."""
    compact_content = " ".join(content.split())
    if len(compact_content) <= PREVIEW_LENGTH:
        return compact_content
    return f"{compact_content[: PREVIEW_LENGTH - 1].rstrip()}…"
