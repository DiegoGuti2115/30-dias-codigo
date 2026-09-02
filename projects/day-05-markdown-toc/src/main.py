"""Command-line integration for the contract-v1 Markdown TOC generator."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
import stat
import sys
from typing import TextIO

from parser import parse_markdown
from rewriter import RewriteError, build_preview, update_file
from toc import build_entries, render_toc

_SUCCESS_MESSAGE = "Índice actualizado."
_UNEXPECTED_ERROR = "Error inesperado."


def build_argument_parser() -> argparse.ArgumentParser:
    """Build the stable v1 command-line parser."""

    parser = argparse.ArgumentParser(
        prog="markdown-toc",
        usage="markdown-toc <DOCUMENT_PATH> [--write]",
        description="Genera o actualiza el índice delimitado de un documento Markdown.",
    )
    parser.add_argument("document_path", metavar="DOCUMENT_PATH")
    parser.add_argument("--write", action="store_true", help="persiste la actualización protegida")
    return parser


def run(
    arguments: Sequence[str] | None = None,
    *,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """Execute one CLI request and return its documented exit status."""

    output = stdout if stdout is not None else sys.stdout
    errors = stderr if stderr is not None else sys.stderr
    parser = build_argument_parser()
    try:
        namespace = parser.parse_args(arguments)
    except SystemExit as error:
        return int(error.code)

    path = Path(namespace.document_path)
    try:
        document = _read_document(path)
        toc = render_toc(build_entries(parse_markdown(document).headings))
        if namespace.write:
            update_file(path, toc)
            output.write(f"{_SUCCESS_MESSAGE}\n")
        else:
            output.write(build_preview(document, toc))
        return 0
    except RewriteError as error:
        errors.write(f"{error}\n")
        return 1
    except OSError:
        errors.write("Error de entrada: no se puede leer el archivo.\n")
        return 1
    except Exception:
        errors.write(f"{_UNEXPECTED_ERROR}\n")
        return 1


def _read_document(path: Path) -> str:
    """Validate and strictly decode a CLI input without modifying it."""

    if path.is_symlink() or not path.is_file():
        raise RewriteError("Error de entrada: se requiere un archivo regular.")
    if path.suffix.lower() not in {".md", ".markdown"}:
        raise RewriteError("Error de entrada: extensión Markdown no admitida.")
    try:
        mode = stat.S_IMODE(path.stat().st_mode)
    except OSError as error:
        raise RewriteError("Error de entrada: no se puede leer el archivo.") from error
    if not mode & 0o444:
        raise RewriteError("Error de entrada: sin permiso de lectura.")
    try:
        raw_document = path.read_bytes()
    except OSError as error:
        raise RewriteError("Error de entrada: no se puede leer el archivo.") from error

    has_bom = raw_document.startswith(b"\xef\xbb\xbf")
    try:
        return raw_document[3:].decode("utf-8") if has_bom else raw_document.decode("utf-8")
    except UnicodeDecodeError as error:
        raise RewriteError("Error de codificación: archivo no UTF-8.") from error


def main() -> int:
    """Run the local command-line entry point without translating preview newlines."""

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(newline="")
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
