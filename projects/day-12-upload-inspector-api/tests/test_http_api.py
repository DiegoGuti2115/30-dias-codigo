"""HTTP contract tests for the Phase 5 FastAPI transport layer."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient
from src import main
from src.schemas import ErrorResponse

INSPECT_PATH = "/api/v1/inspect"
client = TestClient(main.app, raise_server_exceptions=False)


def _upload(
    filename: str = "report.PDF",
    content: bytes = b"Hello, inspector!\n",
    media_type: str = "application/pdf",
) -> dict[str, tuple[str, bytes, str]]:
    return {"file": (filename, content, media_type)}


def _assert_error(response: Any, status_code: int, code: str) -> ErrorResponse:
    assert response.status_code == status_code
    assert response.headers["content-type"] == "application/json; charset=utf-8"
    error = ErrorResponse.model_validate(response.json())
    assert error.error.code == code
    return error


def test_post_inspect_returns_the_documented_response_for_one_valid_file() -> None:
    response = client.post(INSPECT_PATH, files=_upload())

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json; charset=utf-8"
    assert response.json() == {
        "filename": "report.PDF",
        "size_bytes": 18,
        "media_type_declared": "application/pdf",
        "extension": "pdf",
        "filename_checks": {
            "is_safe": True,
            "has_path_separator": False,
            "has_traversal_sequence": False,
            "has_control_characters": False,
            "has_ambiguous_extension": False,
        },
        "content_fingerprint": {
            "algorithm": "sha256",
            "value": "1bf3aefc56ee29340feee1a39a2964489873a899f63796ebe71715d06368a941",
        },
    }


def test_post_inspect_accepts_an_empty_file() -> None:
    response = client.post(INSPECT_PATH, files=_upload(filename="empty.txt", content=b""))

    assert response.status_code == 200
    assert response.json()["size_bytes"] == 0
    assert response.json()["content_fingerprint"]["value"] == (
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )


def test_post_inspect_requires_one_file_part() -> None:
    response = client.post(
        INSPECT_PATH,
        headers={"content-type": "multipart/form-data; boundary=empty"},
        content=b"--empty--\r\n",
    )

    error = _assert_error(response, 422, "validation_error")
    assert error.error.details[0].field == "file"
    assert error.error.details[0].rule == "required"


@pytest.mark.parametrize(
    ("files", "data", "rule"),
    [
        (
            [
                ("file", ("one.txt", b"one", "text/plain")),
                ("file", ("two.txt", b"two", "text/plain")),
            ],
            None,
            "exactly_one",
        ),
        (_upload(), {"note": "extra"}, "extra_field"),
        (_upload(filename="../unsafe.txt"), None, "filename_invalid"),
    ],
)
def test_post_inspect_rejects_invalid_multipart_contract_inputs(
    files: dict[str, tuple[str, bytes, str]] | list[tuple[str, tuple[str, bytes, str]]],
    data: dict[str, str] | None,
    rule: str,
) -> None:
    response = client.post(INSPECT_PATH, files=files, data=data)

    error = _assert_error(response, 422, "validation_error")
    assert error.error.details[0].field == "file"
    assert error.error.details[0].rule == rule
    assert "unsafe.txt" not in error.error.details[0].message


def test_post_inspect_rejects_content_larger_than_five_mebibytes() -> None:
    response = client.post(INSPECT_PATH, files=_upload(content=b"a" * (5 * 1024 * 1024 + 1)))

    error = _assert_error(response, 413, "file_too_large")
    assert [detail.model_dump() for detail in error.error.details] == [
        {
            "field": "file",
            "rule": "max_size",
            "message": "El archivo no puede superar 5 MiB.",
        }
    ]


@pytest.mark.parametrize(
    ("method", "headers", "content", "status_code", "code"),
    [
        ("get", {}, None, 405, "method_not_allowed"),
        ("post", {"content-type": "text/plain"}, b"not multipart", 415, "unsupported_media_type"),
        ("post", {"content-type": "multipart/form-data"}, b"invalid", 400, "malformed_multipart"),
        (
            "post",
            {"content-type": "multipart/form-data; boundary=broken"},
            b"not a valid multipart body",
            400,
            "malformed_multipart",
        ),
    ],
)
def test_http_transport_errors_use_the_public_error_envelope(
    method: str,
    headers: dict[str, str],
    content: bytes | None,
    status_code: int,
    code: str,
) -> None:
    response = client.request(method.upper(), INSPECT_PATH, headers=headers, content=content)

    _assert_error(response, status_code, code)


def test_openapi_documents_the_only_public_multipart_operation() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    operation = response.json()["paths"][INSPECT_PATH]["post"]
    assert set(operation["requestBody"]["content"]) == {"multipart/form-data"}
    assert operation["responses"]["200"]["content"]["application/json; charset=utf-8"]


def test_requests_are_isolated_and_the_same_upload_is_deterministic() -> None:
    first = client.post(INSPECT_PATH, files=_upload())
    intermediate = client.post(INSPECT_PATH, files=_upload(filename="other.txt", content=b"other"))
    repeated = client.post(INSPECT_PATH, files=_upload())

    assert first.json() == repeated.json()
    assert intermediate.json()["filename"] == "other.txt"
