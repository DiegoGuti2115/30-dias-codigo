"""Unit tests for Phase 3 filename normalization and safety rules."""

from __future__ import annotations

import pytest
from src.filename_validation import (
    MAX_FILENAME_CODE_POINTS,
    FilenameValidationError,
    assess_filename,
    derive_extension,
    validate_filename,
)


@pytest.mark.parametrize(
    ("filename", "extension", "is_ambiguous"),
    [
        ("report.PDF", "pdf", False),
        ("archive.tar.gz", "gz", True),
        ("invoice.pdf.exe", "exe", True),
        (".env", None, False),
        (".env.txt", "txt", False),
        ("report.", None, False),
        ("readme", None, False),
    ],
)
def test_derive_extension_follows_the_public_contract(
    filename: str, extension: str | None, is_ambiguous: bool
) -> None:
    assert derive_extension(filename) == (extension, is_ambiguous)


@pytest.mark.parametrize(
    "filename",
    [
        "",
        " \t\n",
        ".",
        "..",
        "../report.txt",
        "folder/report.txt",
        r"folder\report.txt",
        "report\x00.txt",
        "a" * (MAX_FILENAME_CODE_POINTS + 1),
    ],
)
def test_validate_filename_rejects_contract_violations(filename: str) -> None:
    with pytest.raises(FilenameValidationError) as error:
        validate_filename(filename)

    if filename:
        assert filename not in str(error.value)


def test_assessment_preserves_the_received_filename_without_unicode_normalization() -> None:
    filename = "re\u0301sume\u0301.PDF"

    assessment = validate_filename(filename)

    assert assessment.filename == filename
    assert assessment.extension == "pdf"
    assert assessment.is_safe is True


def test_assessment_surfaces_unsafe_indicators_without_path_resolution() -> None:
    assessment = assess_filename("../report.txt")

    assert assessment.is_safe is False
    assert assessment.has_path_separator is True
    assert assessment.has_traversal_sequence is True
    assert assessment.has_control_characters is False
    assert assessment.extension == "txt"


def test_non_string_filename_is_unsafe_without_coercion() -> None:
    assessment = assess_filename(None)

    assert assessment.filename == ""
    assert assessment.is_safe is False
    assert assessment.extension is None
