"""Pydantic models that preserve the public v1 API contract.

These models validate and serialize data only. Text analysis and HTTP error
translation remain intentionally deferred to later roadmap phases.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictSchema(BaseModel):
    """Base schema that rejects properties outside the documented contract."""

    model_config = ConfigDict(extra="forbid")


class AnalyzeRequest(StrictSchema):
    """Body accepted by the future text-analysis operation."""

    text: Annotated[str, Field(min_length=1, max_length=10_000)]


class Metrics(StrictSchema):
    """Non-negative metrics returned for a successfully analyzed text."""

    character_count: Annotated[int, Field(ge=0)]
    character_count_without_whitespace: Annotated[int, Field(ge=0)]
    word_count: Annotated[int, Field(ge=0)]
    sentence_count: Annotated[int, Field(ge=0)]
    paragraph_count: Annotated[int, Field(ge=0)]
    estimated_reading_time_seconds: Annotated[int, Field(ge=0)]


class WordFrequency(StrictSchema):
    """A normalized word and its strictly positive occurrence count."""

    word: Annotated[str, Field(min_length=1)]
    count: Annotated[int, Field(gt=0)]


class AnalyzeResponse(StrictSchema):
    """Successful response shape for the future analysis operation."""

    metrics: Metrics
    word_frequencies: list[WordFrequency]
    keywords: Annotated[list[WordFrequency], Field(max_length=5)]


class ErrorDetail(StrictSchema):
    """A human-readable explanation of one contract violation."""

    field: Annotated[str, Field(min_length=1)]
    rule: Annotated[str, Field(min_length=1)]
    message: Annotated[str, Field(min_length=1)]


class ErrorBody(StrictSchema):
    """The error payload nested under the public ``error`` property."""

    code: Literal[
        "invalid_json",
        "unsupported_media_type",
        "validation_error",
        "method_not_allowed",
        "internal_error",
    ]
    message: Annotated[str, Field(min_length=1)]
    details: list[ErrorDetail] = Field(default_factory=list)


class ErrorResponse(StrictSchema):
    """Uniform public error response defined by the v1 contract."""

    error: ErrorBody
