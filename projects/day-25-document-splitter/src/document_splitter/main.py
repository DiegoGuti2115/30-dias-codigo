"""Command-line entry point for Document Splitter."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from document_splitter.chunkers.text import split_text
from document_splitter.extractors.base import DocumentExtractionError
from document_splitter.extractors.registry import extract_document
from document_splitter.services.results import build_document_result
from document_splitter.utils.files import (
    ResultWritingError,
    default_output_path,
    write_result,
)
from document_splitter.utils.hashing import DocumentHashingError, calculate_document_id
from document_splitter.validators.document import (
    DocumentValidationError,
    validate_document,
)

DEFAULT_CHUNK_SIZE = 1_000
DEFAULT_OVERLAP = 150


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser and its public argument contract."""
    parser = argparse.ArgumentParser(
        prog="document-splitter",
        description="Divide documentos locales en fragmentos trazables.",
    )
    parser.add_argument(
        "source",
        nargs="?",
        type=Path,
        help="Ruta del documento que se validará y del que se extraerá texto.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        metavar="CARACTERES",
        help=f"Máximo de caracteres por fragmento (predeterminado: {DEFAULT_CHUNK_SIZE}).",
    )
    parser.add_argument(
        "--overlap",
        type=int,
        default=DEFAULT_OVERLAP,
        metavar="CARACTERES",
        help=f"Solapamiento entre fragmentos (predeterminado: {DEFAULT_OVERLAP}).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        metavar="RUTA",
        help="Ruta del JSON de salida (predeterminada: output/<archivo>.json).",
    )
    return parser


def parse_args(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments without performing document processing."""
    return build_parser().parse_args(arguments)


def main(arguments: Sequence[str] | None = None) -> int:
    """Validate, extract, fragment, and persist a requested document result."""
    parsed_arguments = parse_args(arguments)

    if parsed_arguments.source is None:
        return 0

    try:
        document = validate_document(
            parsed_arguments.source,
            chunk_size=parsed_arguments.chunk_size,
            overlap=parsed_arguments.overlap,
        )
    except DocumentValidationError as error:
        print(f"Error de validación: {error}", file=sys.stderr)
        return 2

    try:
        text = extract_document(document.path, document.extension)
    except DocumentExtractionError as error:
        print(f"Error de extracción: {error}", file=sys.stderr)
        return 3

    chunks = split_text(
        text,
        chunk_size=parsed_arguments.chunk_size,
        overlap=parsed_arguments.overlap,
    )

    try:
        document_id = calculate_document_id(document.path)
    except DocumentHashingError as error:
        print(f"Error de resultado: {error}", file=sys.stderr)
        return 4

    result = build_document_result(
        source=document.path,
        document_id=document_id,
        chunk_size=parsed_arguments.chunk_size,
        overlap=parsed_arguments.overlap,
        chunks=chunks,
    )
    destination = parsed_arguments.output or default_output_path(document.path)
    try:
        output_path = write_result(result, destination)
    except ResultWritingError as error:
        print(f"Error de resultado: {error}", file=sys.stderr)
        return 4

    print(
        f"Documento fragmentado correctamente: {len(chunks)} fragmentos. "
        f"Salida: {output_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
