"""Safe, non-recursive download sorter for Day 1."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

CATEGORY_BY_EXTENSION = {
    ".png": "Imágenes",
    ".txt": "Documentos",
    ".zip": "Comprimidos",
    ".wav": "Audio",
    ".mp4": "Vídeo",
}


@dataclass(frozen=True)
class SortResult:
    """Outcome recorded for one candidate file."""

    status: str
    source: Path
    destination: Path | None = None
    detail: str | None = None


def sort_downloads(directory: Path, output: TextIO) -> list[SortResult]:
    """Sort top-level regular files in *directory* without overwriting files."""
    directory = directory.expanduser()
    if not directory.is_dir():
        raise ValueError(f"El directorio de entrada no es válido: {directory}")

    directory = directory.resolve()
    results: list[SortResult] = []
    print(f"Directorio de entrada: {directory}", file=output)

    for source in sorted(directory.iterdir(), key=lambda item: item.name.casefold()):
        if not source.is_file():
            continue

        category = CATEGORY_BY_EXTENSION.get(source.suffix.lower())
        if category is None:
            result = SortResult("desconocido", source, detail="extensión no admitida o ausente")
            results.append(result)
            print(f"OMITIDO desconocido: {source.name}", file=output)
            continue

        destination = directory / category / source.name
        if destination.exists():
            result = SortResult("conflicto", source, destination, "el destino ya existe")
            results.append(result)
            print(f"OMITIDO conflicto: {source.name} -> {destination}", file=output)
            continue

        try:
            destination.parent.mkdir(exist_ok=True)
            source.replace(destination)
        except OSError as error:
            result = SortResult("error", source, destination, str(error))
            results.append(result)
            print(f"ERROR: {source.name}: {error}", file=output)
            continue

        result = SortResult("movido", source, destination)
        results.append(result)
        print(f"MOVIDO: {source.name} -> {destination}", file=output)

    counts = Counter(result.status for result in results)
    print(
        "Resumen: "
        f"movidos={counts['movido']}, "
        f"desconocidos={counts['desconocido']}, "
        f"conflictos={counts['conflicto']}, "
        f"errores={counts['error']}",
        file=output,
    )
    return results


def parse_arguments() -> argparse.Namespace:
    """Read the explicitly provided input directory."""
    parser = argparse.ArgumentParser(description="Clasifica descargas por extensión sin sobrescribir archivos.")
    parser.add_argument("directory", type=Path, help="Directorio local que se debe clasificar.")
    return parser.parse_args()


def main() -> int:
    """Run the command-line happy path."""
    arguments = parse_arguments()
    try:
        sort_downloads(arguments.directory, output=sys.stdout)
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
