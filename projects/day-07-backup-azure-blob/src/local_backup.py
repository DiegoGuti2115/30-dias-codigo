"""Phase 3 orchestration for safe local copy, verification, publication, and cleanup."""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Callable

from errors import BackupError, CopyError, PublicationError, VerificationError
from models import BackupPlan, BackupResult
from validation import plan_backup
from verification import VerificationResult, verify_copy

CopyOperation = Callable[[BackupPlan, Path], None]
PublishOperation = Callable[[Path, Path], None]
VerifyOperation = Callable[[Path, Path], VerificationResult]


def _copy_to_temporary(plan: BackupPlan, temporary_path: Path) -> None:
    try:
        if plan.source_is_directory:
            shutil.copytree(plan.source, temporary_path, copy_function=shutil.copyfile)
        else:
            shutil.copyfile(plan.source, temporary_path)
    except OSError as error:
        raise CopyError("local copy could not be completed") from error


def _as_copy_operation(operation: CopyOperation) -> CopyOperation:
    def controlled_copy(plan: BackupPlan, temporary_path: Path) -> None:
        try:
            operation(plan, temporary_path)
        except CopyError:
            raise
        except OSError as error:
            raise CopyError("local copy could not be completed") from error

    return controlled_copy


def _as_publish_operation(operation: PublishOperation) -> PublishOperation:
    def controlled_publish(temporary_path: Path, final_path: Path) -> None:
        try:
            operation(temporary_path, final_path)
        except PublicationError:
            raise
        except OSError as error:
            raise PublicationError("verified copy could not be published") from error

    return controlled_publish


def _publish(temporary_path: Path, final_path: Path) -> None:
    try:
        os.replace(temporary_path, final_path)
    except OSError as error:
        raise PublicationError("verified copy could not be published") from error


def _cleanup_owned_temporary(temporary_path: Path) -> str | None:
    if not temporary_path.exists() and not temporary_path.is_symlink():
        return None
    try:
        if temporary_path.is_dir() and not temporary_path.is_symlink():
            shutil.rmtree(temporary_path)
        else:
            temporary_path.unlink()
    except OSError:
        return "owned temporary artifact could not be removed"
    return None


def _temporary_path(destination: Path) -> Path:
    descriptor, raw_path = tempfile.mkstemp(prefix=".backup-v1-", suffix=".tmp", dir=destination)
    os.close(descriptor)
    path = Path(raw_path)
    path.unlink()
    return path


def run_local_backup(
    source_path: str | Path,
    destination_path: str | Path,
    *,
    copy_operation: CopyOperation = _copy_to_temporary,
    verify_operation: VerifyOperation = verify_copy,
    publish_operation: PublishOperation = _publish,
) -> BackupResult:
    """Run the Phase 3 core without a CLI or any Azure dependency.

    Injected operations are intentionally exposed for deterministic tests of copy,
    verification, and publication failures. They are not a user-facing extension.
    """
    try:
        plan = plan_backup(source_path, destination_path)
    except BackupError as error:
        return BackupResult(False, error_code=error.code, message=str(error))

    temporary_path: Path | None = None
    try:
        temporary_path = _temporary_path(plan.destination)
        _as_copy_operation(copy_operation)(plan, temporary_path)
        verification = verify_operation(plan.source, temporary_path)
        if not verification.valid:
            raise VerificationError(verification.reason or "copy verification failed")
        if plan.final_path.exists() or plan.final_path.is_symlink():
            raise PublicationError("final backup location appeared during operation")
        _as_publish_operation(publish_operation)(temporary_path, plan.final_path)
        temporary_path = None
        return BackupResult(True, final_path=plan.final_path, verification=verification)
    except BackupError as error:
        cleanup_warning = _cleanup_owned_temporary(temporary_path) if temporary_path else None
        return BackupResult(
            False,
            error_code=error.code,
            message=str(error),
            cleanup_warning=cleanup_warning,
        )
    except OSError:
        cleanup_warning = _cleanup_owned_temporary(temporary_path) if temporary_path else None
        return BackupResult(
            False,
            error_code="copy-error",
            message="local backup encountered an operating system error",
            cleanup_warning=cleanup_warning,
        )
