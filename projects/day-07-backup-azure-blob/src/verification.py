"""Ephemeral structure, size, and SHA-256 verification for local backups."""

from __future__ import annotations

import hashlib
import os
import stat
from pathlib import Path

from errors import VerificationError
from models import FileEntry, TreeManifest, VerificationResult

_BUFFER_SIZE = 1024 * 1024


def _is_link_or_junction(path: Path) -> bool:
    try:
        path_stat = path.lstat()
    except OSError:
        return False
    reparse_point = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    attributes = getattr(path_stat, "st_file_attributes", 0)
    return path.is_symlink() or bool(attributes & reparse_point)


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as source:
            for block in iter(lambda: source.read(_BUFFER_SIZE), b""):
                digest.update(block)
    except OSError as error:
        raise VerificationError("a file could not be read during verification") from error
    return digest.hexdigest()


def build_manifest(root: Path) -> TreeManifest:
    """Build a non-persisted manifest and reject links or special entries."""
    try:
        root_stat = root.lstat()
    except OSError as error:
        raise VerificationError("verification root is unavailable") from error

    if _is_link_or_junction(root):
        raise VerificationError("verification root is a symbolic link or junction")
    if stat.S_ISREG(root_stat.st_mode):
        return TreeManifest(
            root_type="regular-file",
            directories=(),
            files=(FileEntry(".", root_stat.st_size, _hash_file(root)),),
        )
    if not stat.S_ISDIR(root_stat.st_mode):
        raise VerificationError("verification root is not a regular file or directory")

    directories = ["."]
    files: list[FileEntry] = []
    try:
        for current, directory_names, file_names in os.walk(root, topdown=True, followlinks=False):
            current_path = Path(current)
            retained_directories: list[str] = []
            for name in sorted(directory_names):
                path = current_path / name
                entry_stat = path.lstat()
                if _is_link_or_junction(path) or not stat.S_ISDIR(entry_stat.st_mode):
                    raise VerificationError("tree contains a symbolic link, junction, or special entry")
                retained_directories.append(name)
                directories.append(path.relative_to(root).as_posix())
            directory_names[:] = retained_directories
            for name in sorted(file_names):
                path = current_path / name
                entry_stat = path.lstat()
                if _is_link_or_junction(path) or not stat.S_ISREG(entry_stat.st_mode):
                    raise VerificationError("tree contains a symbolic link, junction, or special entry")
                files.append(
                    FileEntry(
                        path.relative_to(root).as_posix(),
                        entry_stat.st_size,
                        _hash_file(path),
                    )
                )
    except VerificationError:
        raise
    except OSError as error:
        raise VerificationError("tree could not be read during verification") from error

    return TreeManifest(
        root_type="regular-directory",
        directories=tuple(sorted(directories)),
        files=tuple(sorted(files, key=lambda entry: entry.relative_path)),
    )


def verify_copy(source: Path, copy: Path) -> VerificationResult:
    """Compare source and copy with exact paths, sizes, and per-file SHA-256."""
    try:
        source_manifest = build_manifest(source)
        copy_manifest = build_manifest(copy)
    except VerificationError as error:
        return VerificationResult(False, str(error))

    if source_manifest.root_type != copy_manifest.root_type:
        return VerificationResult(False, "copy root type differs from source")
    if source_manifest.directories != copy_manifest.directories:
        return VerificationResult(False, "copy directory structure differs from source")
    if source_manifest.files != copy_manifest.files:
        return VerificationResult(False, "copy files, sizes, or bytes differ from source")
    return VerificationResult(True)
