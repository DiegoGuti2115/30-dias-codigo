"""Pruebas de carga y validación de configuración de fase uno."""

import json

import pytest

from evaluation_dataset_validator.config.loader import load_validation_settings
from evaluation_dataset_validator.errors import (
    ExitCode,
    FileAccessError,
    InvalidConfigurationError,
)


def test_loads_valid_configuration(tmp_path) -> None:
    source = tmp_path / "settings.json"
    source.write_text(
        json.dumps(
            {
                "required_fields": ["id", "input", "expected_output"],
                "require_unique_ids": False,
                "warn_on_empty_metadata": False,
                "metadata_required_fields_by_task": {"classification": ["label_set"]},
                "disabled_rules": ["semantic_duplicate_input"],
                "rule_severities": {"empty_input": "warning"},
                "max_issues": 3,
            }
        ),
        encoding="utf-8",
    )

    settings = load_validation_settings(source)

    assert settings.require_unique_ids is False
    assert settings.warn_on_empty_metadata is False
    assert settings.metadata_required_fields_by_task == {"classification": ("label_set",)}
    assert settings.disabled_rules == ("semantic_duplicate_input",)
    assert settings.rule_severities["empty_input"].value == "warning"
    assert settings.max_issues == 3


@pytest.mark.parametrize(
    ("content", "expected_detail"),
    [
        ("{", "JSON inválido"),
        ("[]", "la raíz debe ser un objeto JSON"),
        ('{"max_issues": 0}', "max_issues"),
        ('{"unknown": true}', "unknown"),
        ('{"disabled_rules": ["not_a_rule"]}', "reglas desconocidas"),
        ('{"metadata_required_fields_by_task": {"classification": []}}', "al menos un campo"),
    ],
)
def test_rejects_invalid_configuration(
    tmp_path, content: str, expected_detail: str
) -> None:
    source = tmp_path / "settings.json"
    source.write_text(content, encoding="utf-8")

    with pytest.raises(InvalidConfigurationError) as captured:
        load_validation_settings(source)

    assert captured.value.exit_code is ExitCode.CONFIG_ERROR
    assert expected_detail in str(captured.value)


def test_reports_missing_configuration_file(tmp_path) -> None:
    with pytest.raises(FileAccessError) as captured:
        load_validation_settings(tmp_path / "missing.json")

    assert captured.value.exit_code is ExitCode.FILE_ERROR
