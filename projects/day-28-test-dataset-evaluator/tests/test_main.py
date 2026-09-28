"""Pruebas de integración de la CLI de fase uno."""

import json

from evaluation_dataset_validator.errors import ExitCode
from evaluation_dataset_validator.main import run


def _write_dataset(source, records: list[dict]) -> None:
    source.write_text(json.dumps(records), encoding="utf-8")


def test_run_writes_report_and_returns_success(tmp_path, capsys) -> None:
    dataset = tmp_path / "dataset.json"
    report = tmp_path / "nested" / "report.json"
    _write_dataset(
        dataset,
        [{"id": "case-001", "input": "A", "expected_output": "B", "metadata": {}}],
    )
    config = tmp_path / "config.json"
    config.write_text(
        '{"required_fields": ["id", "input", "expected_output"], '
        '"warn_on_empty_metadata": false, "require_unique_ids": true, "max_issues": 10}',
        encoding="utf-8",
    )

    exit_code = run([str(dataset), "--config", str(config), "--report", str(report)])

    assert exit_code is ExitCode.SUCCESS
    assert json.loads(report.read_text(encoding="utf-8"))["is_valid"] is True
    assert "Válido: True" in capsys.readouterr().out


def test_run_returns_validation_error_after_writing_report(tmp_path) -> None:
    dataset = tmp_path / "dataset.json"
    report = tmp_path / "report.json"
    _write_dataset(
        dataset,
        [
            {"id": "duplicate", "input": "A", "expected_output": "B", "metadata": {}},
            {"id": "duplicate", "input": "C", "expected_output": "D", "metadata": {}},
        ],
    )
    config = tmp_path / "config.json"
    config.write_text(
        '{"required_fields": ["id", "input", "expected_output"], "max_issues": 1}',
        encoding="utf-8",
    )

    exit_code = run([str(dataset), "--config", str(config), "--report", str(report)])
    saved_report = json.loads(report.read_text(encoding="utf-8"))

    assert exit_code is ExitCode.VALIDATION_ERRORS
    assert saved_report["is_valid"] is False
    assert saved_report["summary"]["error_count"] == 2
    assert len(saved_report["issues"]) == 1


def test_run_returns_input_error_without_report(tmp_path, capsys) -> None:
    dataset = tmp_path / "bad.json"
    dataset.write_text("[", encoding="utf-8")
    report = tmp_path / "report.json"
    config = tmp_path / "config.json"
    config.write_text('{"required_fields": ["id", "input", "expected_output"]}', encoding="utf-8")

    exit_code = run([str(dataset), "--config", str(config), "--report", str(report)])

    assert exit_code is ExitCode.INVALID_INPUT
    assert report.exists() is False
    assert "JSON inválido" in capsys.readouterr().out


def test_run_returns_config_error(tmp_path, capsys) -> None:
    dataset = tmp_path / "dataset.json"
    _write_dataset(dataset, [])
    config = tmp_path / "config.json"
    config.write_text('{"max_issues": 0}', encoding="utf-8")

    exit_code = run([str(dataset), "--config", str(config)])

    assert exit_code is ExitCode.CONFIG_ERROR
    assert "Configuración inválida" in capsys.readouterr().out


def test_run_applies_phase_two_quality_rules_from_configuration(tmp_path) -> None:
    dataset = tmp_path / "quality.json"
    report = tmp_path / "quality-report.json"
    _write_dataset(
        dataset,
        [
            {
                "id": "first",
                "input": "  ¡HOLA   MUNDO! ",
                "expected_output": "A",
                "metadata": {"task": "classification", "label_set": ["A"]},
            },
            {
                "id": "second",
                "input": "¡hola mundo!",
                "expected_output": "",
                "metadata": {"task": "classification"},
            },
        ],
    )
    config = tmp_path / "config.json"
    config.write_text(
        json.dumps(
            {
                "metadata_required_fields_by_task": {"classification": ["label_set"]},
                "disabled_rules": ["empty_metadata"],
            }
        ),
        encoding="utf-8",
    )

    exit_code = run([str(dataset), "--config", str(config), "--report", str(report)])
    saved_report = json.loads(report.read_text(encoding="utf-8"))

    assert exit_code is ExitCode.VALIDATION_ERRORS
    assert [(issue["code"], issue["severity"]) for issue in saved_report["issues"]] == [
        ("empty_expected_output", "error"),
        ("missing_required_metadata", "error"),
        ("semantic_duplicate_input", "warning"),
    ]
