"""Pruebas de contratos, cobertura y fugas de la fase cuatro."""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from evaluation_dataset_validator.config.settings import ValidationSettings
from evaluation_dataset_validator.errors import ExitCode
from evaluation_dataset_validator.main import run
from evaluation_dataset_validator.validators.dataset import DatasetValidator


def _record(identifier: str, schema: str, input_value: object, output: object, **metadata: object) -> dict:
    return {
        "id": identifier,
        "input": input_value,
        "expected_output": output,
        "metadata": {"task_schema": schema, **metadata},
    }


def _settings(**overrides: object) -> ValidationSettings:
    return ValidationSettings(
        disabled_rules=("empty_metadata", "semantic_duplicate_input", "required_metadata_fields"),
        **overrides,
    )


def test_versioned_task_schemas_accept_valid_text_classification_extraction_and_conversation() -> None:
    records = [
        _record("text", "text/v1", "Pregunta", "Respuesta", evaluator="exact_match"),
        _record("class", "classification/v1", "Texto", "positive", evaluator="label_match", label_set=["positive", "negative"]),
        _record("extract", "extraction/v1", "Ana vive en Madrid", {"person": "Ana"}, evaluator="field_match", extraction_fields=["person"]),
        _record("conversation", "conversation/v1", [{"role": "user", "content": "Hola"}], "Hola", evaluator="turn_match"),
    ]

    report = DatasetValidator(_settings()).validate(records)

    assert report.is_valid is True
    assert report.summary.error_count == 0


def test_schema_rule_reports_wrong_evaluator_output_and_conversation_turn() -> None:
    records = [
        _record("classification", "classification/v1", "Texto", "unknown", evaluator="exact_match", label_set=["positive"]),
        _record("conversation", "conversation/v1", [{"role": "user"}], "Hola", evaluator="turn_match"),
        _record("unknown", "future/v2", "A", "B", evaluator="exact_match"),
    ]

    report = DatasetValidator(_settings()).validate(records)

    assert report.is_valid is False
    assert report.summary.issues_by_code == {"invalid_evaluation_schema": 2, "invalid_evaluator": 1, "unsupported_task_schema": 1}


def test_coverage_and_train_evaluation_leakage_are_deterministic() -> None:
    records = [
        _record("train", "text/v1", "shared", "A", evaluator="exact_match", language="es", category="general", partition="train"),
        _record("test", "text/v1", "shared", "B", evaluator="exact_match", language="en", category="general", partition="test"),
    ]
    settings = _settings(
        coverage_required_values={"metadata.language": ("es", "en", "ca"), "metadata.partition": ("train", "test", "validation")},
        leakage_hash_fields=("input",),
    )

    report = DatasetValidator(settings).validate(records)

    assert report.is_valid is True
    assert report.summary.coverage_by_field == {
        "metadata.language": {"en": 1, "es": 1},
        "metadata.partition": {"test": 1, "train": 1},
    }
    assert report.summary.issues_by_code == {"missing_coverage": 2, "train_evaluation_leakage": 1}
    assert report.issues[-1].record_id == "test"


@pytest.mark.parametrize(
    "settings",
    [
        {"supported_task_schemas": ["unknown/v1"]},
        {"coverage_required_values": {"metadata.unknown": ["x"]}},
        {"leakage_hash_fields": ["id"]},
    ],
)
def test_phase_four_configuration_rejects_unknown_contracts(settings: dict) -> None:
    with pytest.raises(ValidationError):
        ValidationSettings(**settings)


def test_cli_serializes_phase_four_summary_and_returns_validation_error(tmp_path, capsys) -> None:
    dataset = tmp_path / "dataset.json"
    dataset.write_text(json.dumps([_record("train", "text/v1", "shared", "A", evaluator="exact_match", language="es", partition="train"), _record("test", "text/v1", "shared", "B", evaluator="exact_match", language="en", partition="test")]), encoding="utf-8")
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"disabled_rules": ["empty_metadata", "semantic_duplicate_input", "required_metadata_fields"], "coverage_required_values": {"metadata.language": ["es", "en", "ca"]}, "leakage_hash_fields": ["input"], "rule_severities": {"train_evaluation_leakage": "error"}}), encoding="utf-8")
    report = tmp_path / "report.json"

    exit_code = run([str(dataset), "--config", str(config), "--report", str(report), "--output-format", "console"])
    saved = json.loads(report.read_text(encoding="utf-8"))

    assert exit_code is ExitCode.VALIDATION_ERRORS
    assert saved["summary"]["coverage_by_field"] == {"metadata.language": {"en": 1, "es": 1}}
    assert saved["summary"]["issues_by_code"] == {"missing_coverage": 1, "train_evaluation_leakage": 1}
    assert "Cobertura metadata.language: en=1, es=1." in capsys.readouterr().out
