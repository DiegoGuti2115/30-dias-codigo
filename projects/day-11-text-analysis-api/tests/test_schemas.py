"""Contract-focused tests for the Phase 3 Pydantic schemas."""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from src.schemas import AnalyzeRequest, AnalyzeResponse, ErrorResponse


def test_analyze_request_accepts_whitespace_only_text() -> None:
    request = AnalyzeRequest.model_validate({"text": " \t\n "})

    assert request.text == " \t\n "


def test_analyze_request_preserves_text_at_the_maximum_length() -> None:
    text = "a" * 10_000

    request = AnalyzeRequest.model_validate({"text": text})

    assert request.text == text


@pytest.mark.parametrize(
    ("payload", "error_type"),
    [
        ({}, "missing"),
        ({"text": ""}, "string_too_short"),
        ({"text": "a" * 10_001}, "string_too_long"),
        ({"text": 42}, "string_type"),
        ({"text": "valid", "language": "es"}, "extra_forbidden"),
    ],
)
def test_analyze_request_rejects_contract_violations(
    payload: dict[str, object], error_type: str
) -> None:
    with pytest.raises(ValidationError) as error:
        AnalyzeRequest.model_validate(payload)

    assert error.value.errors()[0]["type"] == error_type


def test_analyze_response_serializes_the_documented_shape() -> None:
    response = AnalyzeResponse.model_validate(
        {
            "metrics": {
                "character_count": 4,
                "character_count_without_whitespace": 3,
                "word_count": 1,
                "sentence_count": 1,
                "paragraph_count": 1,
                "estimated_reading_time_seconds": 1,
            },
            "word_frequencies": [{"word": "hola", "count": 1}],
            "keywords": [{"word": "hola", "count": 1}],
        }
    )

    assert response.model_dump() == {
        "metrics": {
            "character_count": 4,
            "character_count_without_whitespace": 3,
            "word_count": 1,
            "sentence_count": 1,
            "paragraph_count": 1,
            "estimated_reading_time_seconds": 1,
        },
        "word_frequencies": [{"word": "hola", "count": 1}],
        "keywords": [{"word": "hola", "count": 1}],
    }


@pytest.mark.parametrize(
    "payload",
    [
        {
            "metrics": {
                "character_count": -1,
                "character_count_without_whitespace": 0,
                "word_count": 0,
                "sentence_count": 0,
                "paragraph_count": 0,
                "estimated_reading_time_seconds": 0,
            },
            "word_frequencies": [],
            "keywords": [],
        },
        {
            "metrics": {
                "character_count": 0,
                "character_count_without_whitespace": 0,
                "word_count": 0,
                "sentence_count": 0,
                "paragraph_count": 0,
                "estimated_reading_time_seconds": 0,
            },
            "word_frequencies": [{"word": "", "count": 1}],
            "keywords": [],
        },
        {
            "metrics": {
                "character_count": 0,
                "character_count_without_whitespace": 0,
                "word_count": 0,
                "sentence_count": 0,
                "paragraph_count": 0,
                "estimated_reading_time_seconds": 0,
            },
            "word_frequencies": [{"word": "valid", "count": 0}],
            "keywords": [],
        },
    ],
)
def test_analyze_response_rejects_invalid_contract_values(payload: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        AnalyzeResponse.model_validate(payload)


def test_analyze_response_rejects_more_than_five_keywords() -> None:
    payload = {
        "metrics": {
            "character_count": 0,
            "character_count_without_whitespace": 0,
            "word_count": 0,
            "sentence_count": 0,
            "paragraph_count": 0,
            "estimated_reading_time_seconds": 0,
        },
        "word_frequencies": [],
        "keywords": [{"word": f"word-{index}", "count": 1} for index in range(6)],
    }

    with pytest.raises(ValidationError) as error:
        AnalyzeResponse.model_validate(payload)

    assert error.value.errors()[0]["type"] == "too_long"


def test_error_response_defaults_to_an_empty_details_list() -> None:
    response = ErrorResponse.model_validate(
        {
            "error": {
                "code": "invalid_json",
                "message": "El cuerpo no puede interpretarse como JSON.",
            }
        }
    )

    assert response.model_dump() == {
        "error": {
            "code": "invalid_json",
            "message": "El cuerpo no puede interpretarse como JSON.",
            "details": [],
        }
    }


def test_error_response_rejects_unknown_codes_and_extra_properties() -> None:
    with pytest.raises(ValidationError):
        ErrorResponse.model_validate(
            {
                "error": {
                    "code": "unknown_error",
                    "message": "Error.",
                    "details": [],
                }
            }
        )

    with pytest.raises(ValidationError) as error:
        ErrorResponse.model_validate(
            {
                "error": {
                    "code": "validation_error",
                    "message": "Solicitud inválida.",
                    "details": [],
                    "trace": "not-public",
                }
            }
        )

    assert error.value.errors()[0]["type"] == "extra_forbidden"
