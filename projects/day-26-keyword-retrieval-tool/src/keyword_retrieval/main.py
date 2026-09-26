"""Command-line interface for local and optional Azure AI Search retrieval."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path
import sys

from keyword_retrieval.azure_search import (
    AzureSearchClient,
    AzureSearchConfig,
    AzureSearchError,
)
from keyword_retrieval.corpus import Document, load_corpus, validate_request
from keyword_retrieval.errors import ValidationError
from keyword_retrieval.presentation import build_azure_response, build_response
from keyword_retrieval.retrieval import retrieve_documents

DEFAULT_CORPUS = Path("data/corpus.json")
DEFAULT_LIMIT = 10
VALIDATION_EXIT_CODE = 2


def build_parser() -> argparse.ArgumentParser:
    """Build the Phase 5 command-line retrieval interface."""
    parser = argparse.ArgumentParser(
        description="Retrieve local keyword matches or optional Azure AI Search results."
    )
    parser.add_argument(
        "query",
        help="Non-whitespace text query to retrieve from the selected provider.",
    )
    parser.add_argument(
        "--provider",
        choices=("local", "azure"),
        default="local",
        help="Retrieval provider (default: %(default)s).",
    )
    parser.add_argument(
        "--corpus",
        type=Path,
        default=DEFAULT_CORPUS,
        help="Path to the local JSON corpus (default: %(default)s).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help="Positive maximum number of results to return (default: %(default)s).",
    )
    parser.add_argument(
        "--format",
        choices=("json",),
        default="json",
        help="Output format (default: %(default)s).",
    )
    return parser


def build_local_response(
    args: argparse.Namespace, documents: tuple[Document, ...]
) -> dict[str, object]:
    """Build the local response from validated corpus documents."""
    results = retrieve_documents(args.query, documents)
    return build_response(
        query=args.query,
        corpus_path=args.corpus.as_posix(),
        document_count=len(documents),
        limit=args.limit,
        output_format=args.format,
        documents=documents,
        results=results,
    )


def build_request_contract(
    args: argparse.Namespace, documents: tuple[Document, ...]
) -> dict[str, object]:
    """Backward-compatible alias for the Phase 4 local response builder."""
    return build_local_response(args, documents)


def build_azure_request_contract(args: argparse.Namespace) -> dict[str, object]:
    """Query Azure AI Search and build its provider-distinct public response."""
    config = AzureSearchConfig.from_environment()
    results = AzureSearchClient(config).search(args.query, args.limit)
    return build_azure_response(
        query=args.query,
        index_name=config.index_name,
        limit=args.limit,
        output_format=args.format,
        results=results,
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Validate, retrieve from the selected provider, and print JSON output."""
    args = build_parser().parse_args(argv)
    try:
        validate_request(args.query, args.limit)
        if args.provider == "azure":
            response = build_azure_request_contract(args)
        else:
            response = build_local_response(args, load_corpus(args.corpus))
    except (ValidationError, AzureSearchError) as error:
        print(
            json.dumps(
                {"error": {"code": error.code, "message": error.message}},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return VALIDATION_EXIT_CODE

    print(json.dumps(response, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
