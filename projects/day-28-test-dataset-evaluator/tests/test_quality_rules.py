"""Pruebas de las reglas de calidad de contenido de fase dos."""

from evaluation_dataset_validator.config.settings import ValidationSettings
from evaluation_dataset_validator.models.contracts import Severity
from evaluation_dataset_validator.validators.dataset import DatasetValidator


def _record(identifier: str, input_value: object, output_value: object, metadata: dict) -> dict:
    return {
        "id": identifier,
        "input": input_value,
        "expected_output": output_value,
        "metadata": metadata,
    }


def test_reports_empty_string_fields_with_configured_severity() -> None:
    settings = ValidationSettings(
        rule_severities={"empty_input": Severity.WARNING},
        disabled_rules=("empty_metadata", "semantic_duplicate_input"),
    )

    report = DatasetValidator(settings).validate(
        [_record("case-001", "  ", "", {"task": "unknown"})]
    )

    assert report.is_valid is False
    assert [(issue.code, issue.severity) for issue in report.issues] == [
        ("empty_input", Severity.WARNING),
        ("empty_expected_output", Severity.ERROR),
    ]


def test_requires_metadata_fields_only_for_configured_task() -> None:
    settings = ValidationSettings(
        metadata_required_fields_by_task={"classification": ("label_set", "locale")},
        disabled_rules=("empty_metadata", "semantic_duplicate_input"),
    )
    report = DatasetValidator(settings).validate(
        [
            _record("missing", "clasifica", "A", {"task": "classification", "label_set": ""}),
            _record("other", "pregunta", "respuesta", {"task": "other"}),
        ]
    )

    assert report.is_valid is False
    assert [(issue.code, issue.field) for issue in report.issues] == [
        ("missing_required_metadata", "metadata.label_set"),
        ("missing_required_metadata", "metadata.locale"),
    ]


def test_detects_unicode_case_and_whitespace_normalized_duplicates() -> None:
    settings = ValidationSettings(
        disabled_rules=(
            "empty_metadata",
            "empty_input",
            "empty_expected_output",
            "required_metadata_fields",
        )
    )
    report = DatasetValidator(settings).validate(
        [
            _record("first", "  ¡HOLA   MUNDO! ", "A", {}),
            _record("second", "¡hola mundo!", "B", {}),
            _record("nested", {"messages": ["hola"]}, "C", {}),
        ]
    )

    assert report.is_valid is True
    assert [(issue.code, issue.record_id) for issue in report.issues] == [
        ("semantic_duplicate_input", "second")
    ]


def test_disabled_rule_and_severity_override_change_result_without_code_changes() -> None:
    settings = ValidationSettings(
        disabled_rules=("empty_expected_output", "empty_metadata", "semantic_duplicate_input"),
        rule_severities={"empty_input": Severity.WARNING},
    )
    report = DatasetValidator(settings).validate([_record("case", "", "", {})])

    assert report.is_valid is True
    assert len(report.issues) == 1
    assert report.issues[0].code == "empty_input"
    assert report.issues[0].severity is Severity.WARNING
