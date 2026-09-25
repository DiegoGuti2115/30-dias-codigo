"""JSON serialization and conflict-safe local result writing."""

from __future__ import annotations

from dataclasses import asdict
import json
import os
from pathlib import Path
import tempfile

from document_splitter.models import DocumentResult


class ResultWritingError(RuntimeError):
    """Raised when a result cannot be serialized or stored safely."""


def default_output_path(source: Path) -> Path:
    """Return the deterministic default JSON target for a validated source."""
    return Path("output") / f"{source.stem}.json"


def serialize_result(result: DocumentResult) -> str:
    """Serialize a result in a stable, readable UTF-8 JSON representation."""
    return json.dumps(asdict(result), ensure_ascii=False, indent=2) + "\n"


def write_result(result: DocumentResult, destination: Path) -> Path:
    """Create ``destination`` atomically without replacing an existing file."""
    target = destination.expanduser().resolve()
    if target.exists():
        raise ResultWritingError(f"El archivo de salida ya existe: {destination}")
    if target.parent.exists() and not target.parent.is_dir():
        raise ResultWritingError(
            f"El directorio de salida no es un directorio: {target.parent}"
        )

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=target.parent,
            prefix=f".{target.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            temporary_file.write(serialize_result(result))

        try:
            os.link(temporary_path, target)
        except FileExistsError as error:
            raise ResultWritingError(
                f"El archivo de salida ya existe: {destination}"
            ) from error
        finally:
            temporary_path.unlink(missing_ok=True)
    except ResultWritingError:
        raise
    except (OSError, TypeError, ValueError) as error:
        raise ResultWritingError(
            f"No se pudo escribir el archivo de salida: {destination}"
        ) from error

    return target
