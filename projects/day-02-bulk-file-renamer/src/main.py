"""Safe, preview-first bulk file renamer for Day 2."""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from fnmatch import fnmatchcase
from pathlib import Path
from typing import Iterable, TextIO

DEFAULT_MANIFEST_NAME = ".bulk-file-renamer-manifest.json"
MANIFEST_VERSION = 1


class RenameError(Exception):
    """Raised when a rename plan is unsafe or cannot be completed."""


@dataclass(frozen=True)
class RenameEntry:
    """One validated source-to-target rename."""

    source: Path
    target: Path


@dataclass(frozen=True)
class RenamePlan:
    """A deterministic set of renames within one directory."""

    directory: Path
    entries: tuple[RenameEntry, ...]


def path_key(path: Path) -> str:
    """Return a Windows-safe key for collision comparisons."""
    return os.path.normcase(str(path.resolve(strict=False))).casefold()


def relative_name(directory: Path, path: Path) -> str:
    """Return a portable manifest name after confirming containment."""
    try:
        return str(path.relative_to(directory))
    except ValueError as error:
        raise RenameError(f"La ruta queda fuera del directorio permitido: {path}") from error


def ensure_directory(directory: Path) -> Path:
    """Validate and normalize the explicitly supplied directory."""
    expanded = directory.expanduser()
    if not expanded.is_dir():
        raise RenameError(f"El directorio de entrada no es válido: {expanded}")
    return expanded.resolve()


def validate_filename(name: str) -> None:
    """Reject names that could escape the directory or are invalid on Windows."""
    forbidden = set('<>:"/\\|?*')
    if not name or name in {".", ".."} or any(character in forbidden for character in name):
        raise RenameError(f"Nombre de destino no válido: {name!r}")
    if name.rstrip(". ") != name:
        raise RenameError(f"Nombre de destino no válido en Windows: {name!r}")


def iter_candidates(directory: Path, pattern: str) -> Iterable[Path]:
    """Yield only top-level, non-symlink regular files matching the glob."""
    for candidate in sorted(directory.iterdir(), key=lambda item: item.name.casefold()):
        if candidate.is_symlink() or not candidate.is_file():
            continue
        if fnmatchcase(candidate.name, pattern):
            yield candidate


def build_rename_plan(directory: Path, find: str, replace: str, pattern: str = "*") -> RenamePlan:
    """Build and completely validate a literal stem-replacement plan."""
    directory = ensure_directory(directory)
    if not find:
        raise RenameError("--find no puede estar vacío para evitar renombrados accidentales.")
    if not pattern:
        raise RenameError("--pattern no puede estar vacío.")

    entries: list[RenameEntry] = []
    for source in iter_candidates(directory, pattern):
        new_stem = source.stem.replace(find, replace)
        if new_stem == source.stem:
            continue
        target_name = f"{new_stem}{source.suffix}"
        validate_filename(target_name)
        entries.append(RenameEntry(source=source, target=directory / target_name))

    plan = RenamePlan(directory=directory, entries=tuple(entries))
    validate_plan(plan)
    return plan


def validate_plan(plan: RenamePlan) -> None:
    """Guarantee that the complete plan cannot overwrite unrelated files."""
    source_keys = {path_key(entry.source) for entry in plan.entries}
    target_keys: set[str] = set()

    for entry in plan.entries:
        if entry.source.parent != plan.directory or entry.target.parent != plan.directory:
            raise RenameError("Todas las rutas del plan deben pertenecer al directorio indicado.")
        if path_key(entry.source) == path_key(entry.target) and entry.source.name != entry.target.name:
            # Case-only changes need staging and are intentionally supported.
            pass
        elif entry.source == entry.target:
            raise RenameError(f"El plan contiene un renombrado sin cambios: {entry.source.name}")

        target_key = path_key(entry.target)
        if target_key in target_keys:
            raise RenameError(f"Dos archivos tendrían el mismo destino: {entry.target.name}")
        target_keys.add(target_key)

        if entry.target.exists() and target_key not in source_keys:
            raise RenameError(f"El destino ya existe y no se sobrescribirá: {entry.target.name}")


def default_manifest_path(directory: Path) -> Path:
    """Return the manifest location selected by the approved scope."""
    return directory / DEFAULT_MANIFEST_NAME


def write_manifest(plan: RenamePlan, manifest_path: Path, operation: str) -> None:
    """Persist a successful operation atomically for later inspection or undo."""
    manifest_path = manifest_path.expanduser().resolve(strict=False)
    if manifest_path.parent != plan.directory:
        raise RenameError("El manifiesto debe guardarse en el directorio de entrada.")
    payload = {
        "version": MANIFEST_VERSION,
        "operation": operation,
        "created_at": datetime.now(UTC).isoformat(),
        "directory": str(plan.directory),
        "entries": [
            {"source": relative_name(plan.directory, entry.source), "target": relative_name(plan.directory, entry.target)}
            for entry in plan.entries
        ],
    }
    temporary = manifest_path.with_name(f".{manifest_path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(manifest_path)
    except OSError as error:
        temporary.unlink(missing_ok=True)
        raise RenameError(f"No se pudo escribir el manifiesto: {error}") from error


def load_undo_plan(manifest_path: Path) -> RenamePlan:
    """Load a completed manifest and create its validated reverse plan."""
    try:
        payload = json.loads(manifest_path.expanduser().read_text(encoding="utf-8"))
        directory = ensure_directory(Path(payload["directory"]))
        entries = tuple(
            RenameEntry(directory / item["target"], directory / item["source"])
            for item in payload["entries"]
        )
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise RenameError(f"El manifiesto no es válido: {manifest_path}") from error

    if payload.get("version") != MANIFEST_VERSION or payload.get("operation") != "rename":
        raise RenameError("El manifiesto no representa una operación de renombrado reversible.")
    plan = RenamePlan(directory, entries)
    validate_plan(plan)
    for entry in entries:
        if not entry.source.exists():
            raise RenameError(f"No se puede deshacer: falta el archivo esperado {entry.source.name}")
    return plan


def execute_plan(plan: RenamePlan) -> None:
    """Execute a validated plan using unique temporary sibling names."""
    if not plan.entries:
        return
    staged: list[tuple[Path, Path, Path]] = []
    try:
        for entry in plan.entries:
            temporary = plan.directory / f".bulk-rename-{uuid.uuid4().hex}.tmp"
            entry.source.replace(temporary)
            staged.append((entry.source, temporary, entry.target))
        for _source, temporary, target in staged:
            temporary.replace(target)
    except OSError as error:
        rollback_errors: list[str] = []
        for source, temporary, target in reversed(staged):
            current = target if target.exists() else temporary
            if not current.exists():
                continue
            try:
                current.replace(source)
            except OSError as rollback_error:
                rollback_errors.append(str(rollback_error))
        suffix = f" Recuperación incompleta: {'; '.join(rollback_errors)}" if rollback_errors else ""
        raise RenameError(f"No se pudo completar el renombrado: {error}.{suffix}") from error


def print_plan(plan: RenamePlan, output: TextIO, action: str) -> None:
    """Render a human-readable preview without mutating the directory."""
    print(f"Directorio: {plan.directory}", file=output)
    print(f"Previsualización ({action}):", file=output)
    if not plan.entries:
        print("  Sin archivos que renombrar.", file=output)
    for entry in plan.entries:
        print(f"  {entry.source.name} -> {entry.target.name}", file=output)
    print(f"Total: {len(plan.entries)}", file=output)


def run_rename(arguments: argparse.Namespace, output: TextIO) -> int:
    """Preview or apply the requested rename operation."""
    plan = build_rename_plan(arguments.directory, arguments.find, arguments.replace, arguments.pattern)
    print_plan(plan, output, "renombrado")
    if not arguments.apply:
        print("No se realizaron cambios. Añada --apply para confirmar.", file=output)
        return 0
    execute_plan(plan)
    manifest = arguments.manifest or default_manifest_path(plan.directory)
    write_manifest(plan, manifest, "rename")
    print(f"Aplicado: {len(plan.entries)}. Manifiesto: {manifest}", file=output)
    return 0


def run_undo(arguments: argparse.Namespace, output: TextIO) -> int:
    """Preview or apply a manifest-backed undo operation."""
    plan = load_undo_plan(arguments.manifest)
    print_plan(plan, output, "deshacer")
    if not arguments.apply:
        print("No se realizaron cambios. Añada --apply para confirmar.", file=output)
        return 0
    execute_plan(plan)
    print(f"Deshecho: {len(plan.entries)}", file=output)
    return 0


def normalize_dash_prefixed_values(argv: list[str]) -> list[str]:
    """Bind dash-prefixed values to --find/--replace before argparse sees them.

    argparse treats a separate token beginning with ``-`` as another option. The
    command's public interface intentionally accepts literal search and
    replacement text such as ``-draft``; normalize only these two known options
    to their equivalent ``--option=value`` representation. Known CLI options
    remain options so missing values still produce argparse's normal error.
    """
    value_options = {"--find", "--replace"}
    known_options = {"--find", "--replace", "--pattern", "--apply", "--manifest", "--help", "-h"}
    normalized: list[str] = []
    index = 0

    while index < len(argv):
        current = argv[index]
        if (
            current in value_options
            and index + 1 < len(argv)
            and argv[index + 1].startswith("-")
            and argv[index + 1] not in known_options
            and argv[index + 1] != "--"
        ):
            normalized.append(f"{current}={argv[index + 1]}")
            index += 2
            continue
        normalized.append(current)
        index += 1
    return normalized


def parse_arguments(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments, including literal values that begin with dashes."""
    parser = argparse.ArgumentParser(description="Renombrador masivo seguro con previsualización predeterminada.")
    commands = parser.add_subparsers(dest="command", required=True)

    rename = commands.add_parser("rename", help="Previsualiza o aplica un reemplazo literal en el nombre base.")
    rename.add_argument("directory", type=Path, help="Directorio local explícito que se procesará.")
    rename.add_argument("--find", required=True, help="Texto literal que se buscará en el nombre sin extensión.")
    rename.add_argument("--replace", required=True, help="Texto literal de reemplazo.")
    rename.add_argument("--pattern", default="*", help="Glob para seleccionar archivos (por defecto: *).")
    rename.add_argument("--apply", action="store_true", help="Aplica el plan mostrado; sin esta opción solo se previsualiza.")
    rename.add_argument("--manifest", type=Path, help="Ruta del manifiesto, dentro del directorio de entrada.")

    undo = commands.add_parser("undo", help="Previsualiza o deshace una operación registrada.")
    undo.add_argument("manifest", type=Path, help="Manifiesto JSON generado por rename --apply.")
    undo.add_argument("--apply", action="store_true", help="Aplica la reversión; sin esta opción solo se previsualiza.")
    raw_arguments = sys.argv[1:] if argv is None else argv
    return parser.parse_args(normalize_dash_prefixed_values(raw_arguments))


def main() -> int:
    """Run the CLI and convert expected safety failures to exit status 2."""
    arguments = parse_arguments()
    try:
        if arguments.command == "rename":
            return run_rename(arguments, sys.stdout)
        return run_undo(arguments, sys.stdout)
    except RenameError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
