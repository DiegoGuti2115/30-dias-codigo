"""End-to-end regression tests for the Phase 6 v1 delivery baseline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import pytest
from fastapi.testclient import TestClient
from src import main
from src.schemas import MAX_FILE_SIZE_BYTES, ErrorResponse, InspectionResponse

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INSPECT_PATH = "/api/v1/inspect"
client = TestClient(main.app, raise_server_exceptions=False)


def _fixture_content() -> bytes:
    return (PROJECT_ROOT / "data" / "fixtures" / "phase-4-sample.txt").read_bytes()


def _expected_fixture_response() -> dict[str, object]:
    expected_path = PROJECT_ROOT / "data" / "expected" / "phase-4-sample.json"
    return cast(dict[str, object], json.loads(expected_path.read_text(encoding="utf-8")))


def _upload(
    filename: str = "phase-4-sample.txt",
    content: bytes | None = None,
    media_type: str = "text/plain",
) -> dict[str, tuple[str, bytes, str]]:
    return {"file": (filename, _fixture_content() if content is None else content, media_type)}


def _assert_error(response: Any, status_code: int, code: str) -> ErrorResponse:
    assert response.status_code == status_code
    assert response.headers["content-type"] == "application/json; charset=utf-8"
    error = ErrorResponse.model_validate(response.json())
    assert error.error.code == code
    return error


def test_http_inspection_matches_the_versioned_safe_fixture() -> None:
    response = client.post(INSPECT_PATH, files=_upload())

    assert response.status_code == 200
    result = InspectionResponse.model_validate(response.json())
    assert result.model_dump() == _expected_fixture_response()


@pytest.mark.parametrize(
    ("filename", "content", "media_type", "extension", "is_ambiguous"),
    [
        ("re\u0301sume\u0301.PDF", b"unicode", "application/example", "pdf", False),
        ("archive.tar.gz", b"archive", "application/gzip", "gz", True),
        (".env", b"metadata", "application/octet-stream", None, False),
    ],
)
def test_http_preserves_safe_metadata_without_interpreting_content(
    filename: str,
    content: bytes,
    media_type: str,
    extension: str | None,
    is_ambiguous: bool,
) -> None:
    response = client.post(INSPECT_PATH, files=_upload(filename, content, media_type))

    assert response.status_code == 200
    result = InspectionResponse.model_validate(response.json())
    assert result.filename == filename
    assert result.media_type_declared == media_type
    assert result.extension == extension
    assert result.filename_checks.has_ambiguous_extension is is_ambiguous


def test_http_accepts_content_at_the_documented_five_mebibyte_limit() -> None:
    content = b"a" * MAX_FILE_SIZE_BYTES

    response = client.post(INSPECT_PATH, files=_upload("limit.bin", content))

    assert response.status_code == 200
    result = InspectionResponse.model_validate(response.json())
    assert result.size_bytes == MAX_FILE_SIZE_BYTES
    assert len(result.content_fingerprint.value) == 64


def test_http_preserves_an_absent_part_media_type_as_null() -> None:
    boundary = "phase-six-boundary"
    body = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="file"; filename="no-media-type.txt"\r\n'
        "\r\n"
        "content without a declared media type\r\n"
        f"--{boundary}--\r\n"
    ).encode()

    response = client.post(
        INSPECT_PATH,
        headers={"content-type": f"multipart/form-data; boundary={boundary}"},
        content=body,
    )

    assert response.status_code == 200
    result = InspectionResponse.model_validate(response.json())
    assert result.media_type_declared is None


@pytest.mark.parametrize("filename", ["..\\private.txt", " "])
def test_http_rejects_hostile_names_without_reflecting_them(filename: str) -> None:
    content = b"confidential payload"
    response = client.post(INSPECT_PATH, files=_upload(filename, content))

    error = _assert_error(response, 422, "validation_error")
    assert error.error.details[0].rule == "filename_invalid"
    assert "private.txt" not in response.text
    assert content.decode() not in response.text


def test_http_translates_unexpected_failures_without_internal_details(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_inspection(*_args: object, **_kwargs: object) -> InspectionResponse:
        raise RuntimeError("sensitive implementation detail")

    monkeypatch.setattr(main, "inspect_file", fail_inspection)
    response = client.post(INSPECT_PATH, files=_upload())

    error = _assert_error(response, 500, "internal_error")
    assert error.error.details == []
    assert "sensitive implementation detail" not in response.text


def test_delivery_requests_remain_isolated_after_error_responses() -> None:
    rejected = client.post(INSPECT_PATH, files=_upload("../invalid.txt", b"bad"))
    accepted = client.post(INSPECT_PATH, files=_upload())
    repeated = client.post(INSPECT_PATH, files=_upload())

    _assert_error(rejected, 422, "validation_error")
    assert accepted.json() == _expected_fixture_response()
    assert repeated.json() == accepted.json()
