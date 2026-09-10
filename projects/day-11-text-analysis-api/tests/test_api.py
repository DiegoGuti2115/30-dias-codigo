"""HTTP contract tests for the Phase 5 FastAPI transport layer."""

from __future__ import annotations

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)
ANALYZE_PATH = "/api/v1/analyze"
JSON_HEADERS = {"content-type": "application/json"}


def test_post_analyze_returns_the_contract_response() -> None:
    response = client.post(ANALYZE_PATH, headers=JSON_HEADERS, json={"text": "Hola, hola mundo."})

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json; charset=utf-8"
    assert response.json() == {
        "metrics": {
            "character_count": 17,
            "character_count_without_whitespace": 15,
            "word_count": 3,
            "sentence_count": 1,
            "paragraph_count": 1,
            "estimated_reading_time_seconds": 1,
        },
        "word_frequencies": [
            {"word": "hola", "count": 2},
            {"word": "mundo", "count": 1},
        ],
        "keywords": [
            {"word": "hola", "count": 2},
            {"word": "mundo", "count": 1},
        ],
    }


def test_post_analyze_accepts_json_with_charset_parameter() -> None:
    response = client.post(
        ANALYZE_PATH,
        headers={"content-type": "application/json; charset=utf-8"},
        content='{"text": " \\t\\n "}',
    )

    assert response.status_code == 200
    assert response.json()["metrics"] == {
        "character_count": 4,
        "character_count_without_whitespace": 0,
        "word_count": 0,
        "sentence_count": 0,
        "paragraph_count": 0,
        "estimated_reading_time_seconds": 0,
    }


def test_post_analyze_rejects_malformed_json() -> None:
    response = client.post(ANALYZE_PATH, headers=JSON_HEADERS, content="{not-json")

    assert response.status_code == 400
    assert response.headers["content-type"] == "application/json; charset=utf-8"
    assert response.json() == {
        "error": {
            "code": "invalid_json",
            "message": "El cuerpo no puede interpretarse como JSON.",
            "details": [
                {
                    "field": "body",
                    "rule": "invalid_json",
                    "message": "El cuerpo no puede interpretarse como JSON.",
                }
            ],
        }
    }


def test_post_analyze_rejects_invalid_payloads() -> None:
    cases = [
        ({}, "text", "required"),
        ({"text": ""}, "text", "min_length"),
        ({"text": 1}, "text", "string_type"),
        ({"text": "valid", "language": "es"}, "language", "extra_field"),
    ]

    for payload, field, rule in cases:
        response = client.post(ANALYZE_PATH, headers=JSON_HEADERS, json=payload)

        assert response.status_code == 422
        body = response.json()
        assert body["error"]["code"] == "validation_error"
        assert body["error"]["details"][0]["field"] == field
        assert body["error"]["details"][0]["rule"] == rule


def test_post_analyze_rejects_non_json_content() -> None:
    response = client.post(
        ANALYZE_PATH,
        headers={"content-type": "text/plain"},
        content="texto",
    )

    assert response.status_code == 415
    assert response.json() == {
        "error": {
            "code": "unsupported_media_type",
            "message": "La solicitud debe usar application/json.",
            "details": [],
        }
    }


def test_analyze_rejects_another_http_method() -> None:
    response = client.get(ANALYZE_PATH)

    assert response.status_code == 405
    assert response.json() == {
        "error": {
            "code": "method_not_allowed",
            "message": "El método HTTP no está permitido para esta ruta.",
            "details": [],
        }
    }


def test_openapi_documents_the_single_analysis_operation() -> None:
    specification = client.get("/openapi.json").json()

    assert specification["info"]["title"] == "API de análisis de texto"
    assert specification["info"]["version"] == "1.0.0"
    assert set(specification["paths"]) == {ANALYZE_PATH}
    assert set(specification["paths"][ANALYZE_PATH]) == {"post"}
