"""Strict Pydantic schemas for the public v1 inspection contract.

They define representation and validation only. Multipart parsing, byte-size
limits, SHA-256 calculation, and HTTP response translation remain deferred to
later phases.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictInt,
    field_validator,
    model_validator,
)
from src.filename_validation import MAX_FILENAME_CODE_POINTS, assess_filename, validate_filename

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024


class StrictSchema(BaseModel):
    """Base model that rejects undeclared data and does not coerce values."""

    model_config = ConfigDict(extra="forbid", strict=True)


class FilenameChecks(StrictSchema):
    """Public safety indicators for a successfully validated filename."""

    is_safe: StrictBool
    has_path_separator: StrictBool
    has_traversal_sequence: StrictBool
    has_control_characters: StrictBool
    has_ambiguous_extension: StrictBool

    @field_validator("is_safe")
    @classmethod
    def require_safe_filename(cls, value: bool) -> bool:
        """A successful inspection response can only contain a safe name."""

        if not value:
            raise ValueError("is_safe must be true in a successful response")
        return value

    @field_validator(
        "has_path_separator", "has_traversal_sequence", "has_control_characters"
    )
    @classmethod
    def reject_unsafe_indicators(cls, value: bool) -> bool:
        """Unsafe indicators are invalid once a response is successful."""

        if value:
            raise ValueError("unsafe filename indicators must be false in a successful response")
        return value


class ContentFingerprint(StrictSchema):
    """The fixed SHA-256 representation guaranteed by version 1."""

    algorithm: Literal["sha256"]
    value: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


class InspectionResponse(StrictSchema):
    """Successful response representation for the future inspect operation."""

    filename: Annotated[str, Field(min_length=1, max_length=MAX_FILENAME_CODE_POINTS)]
    size_bytes: Annotated[StrictInt, Field(ge=0, le=MAX_FILE_SIZE_BYTES)]
    media_type_declared: str | None
    extension: str | None
    filename_checks: FilenameChecks
    content_fingerprint: ContentFingerprint

    @field_validator("filename")
    @classmethod
    def require_safe_filename(cls, value: str) -> str:
        """Preserve the original name while applying the contract safety rules."""

        validate_filename(value)
        return value

    @field_validator("extension")
    @classmethod
    def validate_extension(cls, value: str | None) -> str | None:
        """Require the normalized suffix form defined by the public contract."""

        if value is None:
            return None
        if not value or "." in value or value != value.lower():
            raise ValueError("extension must be a lowercase suffix without dots")
        return value

    @model_validator(mode="after")
    def require_filename_metadata_consistency(self) -> InspectionResponse:
        """Prevent a response from contradicting its received filename."""

        assessment = assess_filename(self.filename)
        expected_checks = {
            "is_safe": assessment.is_safe,
            "has_path_separator": assessment.has_path_separator,
            "has_traversal_sequence": assessment.has_traversal_sequence,
            "has_control_characters": assessment.has_control_characters,
            "has_ambiguous_extension": assessment.has_ambiguous_extension,
        }
        if self.filename_checks.model_dump() != expected_checks:
            raise ValueError("filename_checks must match the received filename")
        if self.extension != assessment.extension:
            raise ValueError("extension must match the received filename")
        return self


class ErrorDetail(StrictSchema):
    """One generic, safe explanation for a public contract violation."""

    field: Annotated[str, Field(min_length=1)]
    rule: Annotated[str, Field(min_length=1)]
    message: Annotated[str, Field(min_length=1)]


class ErrorBody(StrictSchema):
    """The error envelope content defined by the public contract."""

    code: Literal[
        "malformed_multipart",
        "file_too_large",
        "unsupported_media_type",
        "validation_error",
        "method_not_allowed",
        "internal_error",
    ]
    message: Annotated[str, Field(min_length=1)]
    details: list[ErrorDetail] = Field(default_factory=list)


class ErrorResponse(StrictSchema):
    """Uniform public error response returned by a future HTTP layer."""

    error: ErrorBody
