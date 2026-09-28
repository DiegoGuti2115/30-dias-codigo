"""Pruebas reproducibles para las validaciones iniciales."""

from evaluation_dataset_validator.validators.dataset import DatasetValidator


def test_accepts_valid_dataset() -> None:
    report = DatasetValidator().validate(
        [
            {
                "id": "case-001",
                "input": "Hola",
                "expected_output": "Un saludo",
                "metadata": {"locale": "es"},
            }
        ]
    )

    assert report.is_valid is True
    assert report.summary.valid_records == 1
    assert report.issues == []


def test_reports_duplicate_identifiers_and_empty_metadata() -> None:
    report = DatasetValidator().validate(
        [
            {"id": "case-001", "input": "A", "expected_output": "B", "metadata": {}},
            {"id": "case-001", "input": "C", "expected_output": "D", "metadata": {}},
        ]
    )

    assert report.is_valid is False
    assert report.summary.error_count == 2
    assert report.summary.warning_count == 2
    assert {issue.code for issue in report.issues} == {"duplicate_id", "empty_metadata"}


def test_reports_invalid_schema_without_interrupting_execution() -> None:
    report = DatasetValidator().validate([{"id": "case-001", "input": "sin salida"}])

    assert report.is_valid is False
    assert report.summary.total_records == 1
    assert report.summary.error_count == 1
    assert report.issues[0].code == "invalid_schema"
