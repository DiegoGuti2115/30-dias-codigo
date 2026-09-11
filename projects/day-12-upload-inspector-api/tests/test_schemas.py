"""Contract-focused tests for the Phase 3 Pydantic schemas."""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from src.schemas import MAX_FILE_SIZE_BYTES, ErrorResponse, InspectionResponse

SHA256_VALUE = "0" * 64


def _valid_response_payload() -> dict[str, object]:
    return {
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
        "content_fingerprint": {"algorithm": "sha256", "value": SHA256_VALUE},
    }


def test_inspection_response_serializes_the_documented_shape() -> None:
    response = InspectionResponse.model_validate(_valid_response_payload())

    assert response.model_dump() == _valid_response_payload()


def test_inspection_response_accepts_an_empty_file_representation() -> None:
    payload = _valid_response_payload()
    payload["filename"] = "empty.txt"
    payload["size_bytes"] = 0
    payload["extension"] = "txt"

    response = InspectionResponse.model_validate(payload)

    assert response.size_bytes == 0


@pytest.mark.parametrize(
    "mutate_payload",
    [
        lambda payload: payload.update(size_bytes=-1),
        lambda payload: payload.update(size_bytes=MAX_FILE_SIZE_BYTES + 1),
        lambda payload: payload.update(filename="../report.txt"),
        lambda payload: payload.update(extension="PDF"),
        lambda payload: payload["content_fingerprint"].update(value="not-a-sha256"),
        lambda payload: payload["filename_checks"].update(has_ambiguous_extension=True),
    ],
)
def test_inspection_response_rejects_invalid_or_inconsistent_values(
    mutate_payload: object,
) -> None:
    payload = _valid_response_payload()
    mutate_payload(payload)  # type: ignore[operator]

    with pytest.raises(ValidationError):
        InspectionResponse.model_validate(payload)


def test_inspection_response_requires_ambiguous_extension_indicator_to_match_name() -> None:
    payload = _valid_response_payload()
    payload["filename"] = "invoice.pdf.exe"
    payload["extension"] = "exe"
    payload["filename_checks"] = {
        "is_safe": True,
        "has_path_separator": False,
        "has_traversal_sequence": False,
        "has_control_characters": False,
        "has_ambiguous_extension": True,
    }

    response = InspectionResponse.model_validate(payload)

    assert response.filename_checks.has_ambiguous_extension is True


def test_error_response_defaults_to_an_empty_details_list() -> None:
    response = ErrorResponse.model_validate(
        {"error": {"code": "validation_error", "message": "Solicitud inválida."}}
    )

    assert response.model_dump()["error"]["details"] == []


def test_error_response_rejects_unknown_codes_and_extra_properties() -> None:
    with pytest.raises(ValidationError):
        ErrorResponse.model_validate(
            {"error": {"code": "unknown_error", "message": "Error.", "details": []}}
        )

    with pytest.raises(ValidationError):
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
