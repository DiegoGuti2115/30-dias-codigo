"""Domain errors whose messages are safe to return from the local core."""

from __future__ import annotations


class BackupError(Exception):
    """Base error for a controlled, non-destructive backup failure."""

    code = "backup-error"


class ValidationError(BackupError):
    code = "validation-error"


class CopyError(BackupError):
    code = "copy-error"


class VerificationError(BackupError):
    code = "verification-error"


class PublicationError(BackupError):
    code = "publication-error"
