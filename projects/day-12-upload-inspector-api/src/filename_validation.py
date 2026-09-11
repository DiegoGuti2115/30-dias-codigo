"""Pure, contract-driven filename and extension validation utilities.

The functions in this module never access the filesystem and never treat an
uploaded filename as a path. HTTP concerns and file-content inspection belong
to later roadmap phases.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass

MAX_FILENAME_CODE_POINTS = 255
_PATH_SEPARATORS = frozenset({"/", "\\"})


class FilenameValidationError(ValueError):
    """Raised when an untrusted filename violates the public v1 contract."""


@dataclass(frozen=True, slots=True)
class FilenameAssessment:
    """Deterministic filename metadata derived without filesystem access."""

    filename: str
    is_safe: bool
    has_path_separator: bool
    has_traversal_sequence: bool
    has_control_characters: bool
    has_ambiguous_extension: bool
    extension: str | None


def assess_filename(filename: object) -> FilenameAssessment:
    """Return all public filename indicators for an untrusted input.

    This function deliberately preserves the input string exactly. It does not
    normalize Unicode, resolve paths, infer a content type, or inspect a file.
    Non-string values are represented as unsafe rather than coerced.
    """

    if not isinstance(filename, str):
        return FilenameAssessment(
            filename="",
            is_safe=False,
            has_path_separator=False,
            has_traversal_sequence=False,
            has_control_characters=False,
            has_ambiguous_extension=False,
            extension=None,
        )

    has_path_separator = any(character in _PATH_SEPARATORS for character in filename)
    has_traversal_sequence = _has_traversal_sequence(filename)
    has_control_characters = any(
        unicodedata.category(character) == "Cc" for character in filename
    )
    extension, has_ambiguous_extension = derive_extension(filename)
    is_safe = (
        1 <= len(filename) <= MAX_FILENAME_CODE_POINTS
        and not filename.isspace()
        and filename not in {".", ".."}
        and not has_path_separator
        and not has_traversal_sequence
        and not has_control_characters
    )

    return FilenameAssessment(
        filename=filename,
        is_safe=is_safe,
        has_path_separator=has_path_separator,
        has_traversal_sequence=has_traversal_sequence,
        has_control_characters=has_control_characters,
        has_ambiguous_extension=has_ambiguous_extension,
        extension=extension,
    )


def validate_filename(filename: object) -> FilenameAssessment:
    """Require a filename that satisfies all v1 safety rules.

    The exception intentionally contains no supplied filename so future HTTP
    error handling can expose a generic message without leaking client input.
    """

    assessment = assess_filename(filename)
    if not assessment.is_safe:
        raise FilenameValidationError("filename does not satisfy the v1 safety rules")
    return assessment


def derive_extension(filename: str) -> tuple[str | None, bool]:
    """Derive the contract's normalized extension and ambiguity indicator."""

    last_dot = filename.rfind(".")
    if last_dot == -1 or last_dot == len(filename) - 1 or last_dot == 0:
        return None, False

    extension = filename[last_dot + 1 :].lower()
    significant_dots = [
        index for index, character in enumerate(filename) if character == "." and index
    ]
    has_ambiguous_extension = len(significant_dots) > 1
    return extension, has_ambiguous_extension


def _has_traversal_sequence(filename: str) -> bool:
    """Detect a ``..`` path segment without resolving or normalizing a path."""

    return ".." in filename.replace("\\", "/").split("/")


