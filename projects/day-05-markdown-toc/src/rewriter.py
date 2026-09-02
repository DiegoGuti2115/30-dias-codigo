"""Protected preview and persistence for the contract-v1 TOC block."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
import stat
import tempfile

START_MARKER = "<!-- markdown-toc:start -->"
END_MARKER = "<!-- markdown-toc:end -->"
_MARKER_LIKE = re.compile(r"markdown-toc:(?:start|end)", re.IGNORECASE)
_NEWLINE = re.compile(r"\r\n|\n|\r")


class RewriteError(ValueError):
    """A deterministic contract or persistence error for the TOC rewriter."""


@dataclass(frozen=True)
class BlockRegion:
    """Character offsets for the replaceable interior of a valid TOC block."""

    content_start: int
    content_end: int
    newline: str


@dataclass(frozen=True)
class RewriteResult:
    """Outcome of a protected file update."""

    document: str
    changed: bool


def locate_block(document: str) -> BlockRegion:
    """Validate and return the sole contract-v1 TOC block in *document*."""

    lines = document.splitlines(keepends=True)
    offsets: list[int] = []
    position = 0
    for line in lines:
        offsets.append(position)
        position += len(line)

    exact_starts: list[int] = []
    exact_ends: list[int] = []
    invalid_marker = False
    for index, line in enumerate(lines):
        visible_line = line.rstrip("\r\n")
        if visible_line == START_MARKER:
            exact_starts.append(index)
        elif visible_line == END_MARKER:
            exact_ends.append(index)
        elif _MARKER_LIKE.search(visible_line):
            invalid_marker = True

    if invalid_marker:
        raise RewriteError("Bloque de índice inválido.")
    if len(exact_starts) > 1 or len(exact_ends) > 1:
        raise RewriteError("Bloque de índice duplicado.")
    if not exact_starts and not exact_ends:
        raise RewriteError("Bloque de índice ausente.")
    if not exact_starts or not exact_ends:
        raise RewriteError("Bloque de índice incompleto.")

    start_index = exact_starts[0]
    end_index = exact_ends[0]
    if end_index < start_index:
        raise RewriteError("Bloque de índice invertido.")

    content_start = offsets[start_index] + len(lines[start_index])
    content_end = offsets[end_index]
    newline_match = _NEWLINE.search(document)
    return BlockRegion(content_start, content_end, newline_match.group(0) if newline_match else "\n")


def build_preview(document: str, toc: str) -> str:
    """Return the proposed document without persisting any change.

    Only the content interior to the validated block is replaced. The supplied TOC
    must use LF internally, as produced by :func:`toc.render_toc`.
    """

    region = locate_block(document)
    replacement = _replacement_content(toc, region.newline)
    return document[: region.content_start] + replacement + document[region.content_end :]


def update_file(path: Path, toc: str) -> RewriteResult:
    """Atomically replace a valid block in *path*, or leave the original intact.

    This Phase 4 API accepts one already-selected local document. CLI argument
    handling belongs to Phase 5, but resource, encoding, and write safeguards are
    enforced here so persistence itself cannot perform a partial update.
    """

    document_path = Path(path)
    _validate_document_path(document_path)
    raw_document = _read_utf8(document_path)
    has_bom = raw_document.startswith(b"\xef\xbb\xbf")
    try:
        document = raw_document[3:].decode("utf-8") if has_bom else raw_document.decode("utf-8")
    except UnicodeDecodeError as error:
        raise RewriteError("Error de codificación: archivo no UTF-8.") from error
    proposed = build_preview(document, toc)

    if proposed == document:
        return RewriteResult(document=document, changed=False)

    _ensure_writable(document_path)
    encoded = (b"\xef\xbb\xbf" if has_bom else b"") + proposed.encode("utf-8")
    _atomic_replace(document_path, encoded)
    return RewriteResult(document=proposed, changed=True)


def _replacement_content(toc: str, newline: str) -> str:
    if not toc:
        return ""
    return toc.replace("\n", newline) + newline


def _validate_document_path(path: Path) -> None:
    if path.is_symlink() or not path.is_file():
        raise RewriteError("Error de entrada: se requiere un archivo regular.")
    if path.suffix.lower() not in {".md", ".markdown"}:
        raise RewriteError("Error de entrada: extensión Markdown no admitida.")


def _read_utf8(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except OSError as error:
        raise RewriteError("Error de entrada: no se puede leer el archivo.") from error


def _ensure_writable(path: Path) -> None:
    try:
        mode = stat.S_IMODE(path.stat().st_mode)
    except OSError as error:
        raise RewriteError("Error de actualización: no se puede comprobar el archivo.") from error
    if not mode & 0o222:
        raise RewriteError("Error de actualización: sin permiso de escritura.")


def _atomic_replace(path: Path, content: bytes) -> None:
    descriptor: int | None = None
    temporary_name: str | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        with os.fdopen(descriptor, "wb") as temporary:
            descriptor = None
            temporary.write(content)
            temporary.flush()
            os.fsync(temporary.fileno())
        os.chmod(temporary_name, stat.S_IMODE(path.stat().st_mode))
        os.replace(temporary_name, path)
        temporary_name = None
    except OSError as error:
        raise RewriteError("Error de actualización: no se pudo persistir el archivo.") from error
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if temporary_name is not None:
            try:
                os.unlink(temporary_name)
            except OSError:
                pass
