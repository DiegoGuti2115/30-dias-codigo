"""End-to-end regression tests required by Phase 6."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import pytest
from fastapi.testclient import TestClient
from src import main
from src.schemas import ErrorResponse

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ANALYZE_PATH = "/api/v1/analyze"
JSON_HEADERS = {"content-type": "application/json"}
client = TestClient(main.app)


def _fixture_text() -> str:
    return (PROJECT_ROOT / "data" / "fixtures" / "contract-example.txt").read_text(
        encoding="utf-8"
    )


def _expected_fixture_response() -> dict[str, Any]:
    payload = json.loads(
        (PROJECT_ROOT / "data" / "expected" / "contract-example.json").read_text(
            encoding="utf-8"
        )
    )
    return cast(dict[str, Any], payload)


def test_http_analysis_matches_the_versioned_fixture_result() -> None:
    response = client.post(ANALYZE_PATH, headers=JSON_HEADERS, json={"text": _fixture_text()})

    assert response.status_code == 200
    assert response.json() == _expected_fixture_response()


def test_http_analysis_accepts_the_documented_maximum_text_length() -> None:
    text = "a" * 10_000
    response = client.post(ANALYZE_PATH, headers=JSON_HEADERS, json={"text": text})

    assert response.status_code == 200
    assert response.json() == {
        "metrics": {
            "character_count": 10_000,
            "character_count_without_whitespace": 10_000,
            "word_count": 1,
            "sentence_count": 1,
            "paragraph_count": 1,
            "estimated_reading_time_seconds": 1,
        },
        "word_frequencies": [{"word": text, "count": 1}],
        "keywords": [{"word": text, "count": 1}],
    }


def test_http_validation_rejects_text_above_the_limit_without_running_analysis(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_if_called(_text: str) -> Any:
        raise AssertionError("The analyzer must not run for an invalid request.")

    monkeypatch.setattr(main, "analyze_text", fail_if_called)

    response = client.post(ANALYZE_PATH, headers=JSON_HEADERS, json={"text": "a" * 10_001})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert response.json()["error"]["details"] == [
        {
            "field": "text",
            "rule": "max_length",
            "message": "text no puede superar 10.000 caracteres.",
        }
    ]


@pytest.mark.parametrize(
    ("method", "headers", "content", "expected_status", "expected_code"),
    [
        ("post", JSON_HEADERS, "{", 400, "invalid_json"),
        ("post", {"content-type": "text/plain"}, "texto", 415, "unsupported_media_type"),
        ("get", {}, None, 405, "method_not_allowed"),
    ],
)
def test_http_errors_keep_the_public_error_schema(
    method: str,
    headers: dict[str, str],
    content: str | None,
    expected_status: int,
    expected_code: str,
) -> None:
    response = client.request(method.upper(), ANALYZE_PATH, headers=headers, content=content)

    assert response.status_code == expected_status
    assert response.headers["content-type"] == "application/json; charset=utf-8"
    assert ErrorResponse.model_validate(response.json()).error.code == expected_code


def test_http_requests_are_isolated_and_fixture_results_are_repeatable() -> None:
    first = client.post(ANALYZE_PATH, headers=JSON_HEADERS, json={"text": _fixture_text()})
    intermediate = client.post(ANALYZE_PATH, headers=JSON_HEADERS, json={"text": "único"})
    repeated = client.post(ANALYZE_PATH, headers=JSON_HEADERS, json={"text": _fixture_text()})

    assert first.json() == _expected_fixture_response()
    assert repeated.json() == _expected_fixture_response()
    assert intermediate.json()["word_frequencies"] == [{"word": "único", "count": 1}]
