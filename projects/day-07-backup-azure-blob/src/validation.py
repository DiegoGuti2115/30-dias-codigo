"""Validation and planning for a single local backup operation."""

from __future__ import annotations

import os
import stat
from pathlib import Path

from errors import ValidationError
from models import BackupPlan


def _normalise(path: str | Path) -> Path:
    """Make a path absolute without resolving links that the contract must reject."""
    return Path(os.path.abspath(Path(path).expanduser()))


def _is_link_or_junction(path: Path) -> bool:
    try:
        path_stat = path.lstat()
    except OSError:
        return False
    reparse_point = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    attributes = getattr(path_stat, "st_file_attributes", 0)
    return path.is_symlink() or bool(attributes & reparse_point)


def _is_regular_file(path: Path) -> bool:
    try:
        return stat.S_ISREG(path.lstat().st_mode) and not _is_link_or_junction(path)
    except OSError:
        return False


def _is_regular_directory(path: Path) -> bool:
    try:
        return stat.S_ISDIR(path.lstat().st_mode) and not _is_link_or_junction(path)
    except OSError:
        return False


def _is_within(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
    except ValueError:
        return False
    return True


def _ensure_readable_file(path: Path) -> None:
    try:
        with path.open("rb"):
            pass
    except OSError as error:
        raise ValidationError("source is not readable") from error


def _scan_directory(source: Path) -> None:
    """Reject links and all non-regular entries before any copy begins."""
    try:
        with os.scandir(source) as entries:
            for entry in entries:
                entry_path = Path(entry.path)
                if _is_link_or_junction(entry_path):
                    raise ValidationError("source tree contains a symbolic link or junction")
                entry_stat = entry.stat(follow_symlinks=False)
                if stat.S_ISDIR(entry_stat.st_mode):
                    _scan_directory(entry_path)
                elif stat.S_ISREG(entry_stat.st_mode):
                    _ensure_readable_file(entry_path)
                else:
                    raise ValidationError("source tree contains an unsupported filesystem entry")
    except ValidationError:
        raise
    except OSError as error:
        raise ValidationError("source directory is not readable") from error


def plan_backup(source_path: str | Path, destination_path: str | Path) -> BackupPlan:
    """Return a fully validated plan without creating or changing any filesystem entry."""
    source = _normalise(source_path)
    destination = _normalise(destination_path)

    if not source.exists() and not source.is_symlink():
        raise ValidationError("source does not exist")
    if _is_link_or_junction(source):
        raise ValidationError("source symbolic links and junctions are not supported")

    source_is_directory = _is_regular_directory(source)
    if not source_is_directory and not _is_regular_file(source):
        raise ValidationError("source must be a regular file or directory")
    if source_is_directory:
        _scan_directory(source)
    else:
        _ensure_readable_file(source)

    if not destination.exists() and not destination.is_symlink():
        raise ValidationError("destination does not exist")
    if _is_link_or_junction(destination) or not _is_regular_directory(destination):
        raise ValidationError("destination must be an existing regular directory")
    if not os.access(destination, os.W_OK | os.X_OK):
        raise ValidationError("destination is not writable")

    final_path = destination / source.name
    if final_path.exists() or _is_link_or_junction(final_path):
        raise ValidationError("final backup location already exists")
    if source == final_path:
        raise ValidationError("source and final backup location must differ")
    if source_is_directory and (_is_within(destination, source) or _is_within(source, destination)):
        raise ValidationError("destination cannot be inside or above a directory source")

    return BackupPlan(
        source=source,
        destination=destination,
        final_path=final_path,
        source_is_directory=source_is_directory,
    )
