"""Structured values for the Phase 3 local backup core."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BackupPlan:
    """A validated local operation with no filesystem mutation performed yet."""

    source: Path
    destination: Path
    final_path: Path
    source_is_directory: bool


@dataclass(frozen=True)
class FileEntry:
    """An in-memory regular-file description used only while verifying a copy."""

    relative_path: str
    size_bytes: int
    sha256: str


@dataclass(frozen=True)
class TreeManifest:
    """In-memory manifest; hashes are deliberately never persisted by this module."""

    root_type: str
    directories: tuple[str, ...]
    files: tuple[FileEntry, ...]


@dataclass(frozen=True)
class VerificationResult:
    valid: bool
    reason: str | None = None


@dataclass(frozen=True)
class RemoteBackupResult:
    """Controlled optional-destination result that never contains provider details."""

    success: bool
    uploaded_blobs: int = 0
    message: str | None = None


@dataclass(frozen=True)
class BackupResult:
    """Controlled result returned by the core instead of exposing filesystem exceptions."""

    success: bool
    final_path: Path | None = None
    verification: VerificationResult | None = None
    error_code: str | None = None
    message: str | None = None
    cleanup_warning: str | None = None
