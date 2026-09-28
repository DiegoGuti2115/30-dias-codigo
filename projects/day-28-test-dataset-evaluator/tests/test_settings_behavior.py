"""Pruebas de los límites y opciones aplicados por el validador."""

from evaluation_dataset_validator.config.settings import ValidationSettings
from evaluation_dataset_validator.validators.dataset import DatasetValidator


def test_configuration_can_disable_optional_rules_and_uniqueness() -> None:
    settings = ValidationSettings(
        require_unique_ids=False,
        warn_on_empty_metadata=False,
        max_issues=10,
    )

    report = DatasetValidator(settings).validate(
        [
            {"id": "same", "input": "A", "expected_output": "B", "metadata": {}},
            {"id": "same", "input": "C", "expected_output": "D", "metadata": {}},
        ]
    )

    assert report.is_valid is True
    assert report.issues == []


def test_max_issues_limits_output_but_not_validation_state_or_summary() -> None:
    settings = ValidationSettings(max_issues=1)
    report = DatasetValidator(settings).validate(
        [
            {"id": "same", "input": "A", "expected_output": "B", "metadata": {}},
            {"id": "same", "input": "C", "expected_output": "D", "metadata": {}},
        ]
    )

    assert report.is_valid is False
    assert report.summary.total_records == 2
    assert report.summary.error_count == 2
    assert report.summary.warning_count == 2
    assert len(report.issues) == 1
