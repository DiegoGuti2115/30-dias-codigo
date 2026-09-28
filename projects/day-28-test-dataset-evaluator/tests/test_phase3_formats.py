"""Pruebas de adaptadores, ubicaciones y serializadores de fase tres."""

import csv
import json

import pytest

from evaluation_dataset_validator.config.settings import ValidationSettings
from evaluation_dataset_validator.errors import InvalidDatasetError, InvalidJsonError
from evaluation_dataset_validator.main import run
from evaluation_dataset_validator.reporting.formatters import write_csv_report, write_sarif_report
from evaluation_dataset_validator.services.dataset_loader import load_dataset
from evaluation_dataset_validator.validators.dataset import DatasetValidator


def _settings() -> ValidationSettings:
    return ValidationSettings(
        metadata_required_fields_by_task={"classification": ("label_set",)},
        disabled_rules=("empty_metadata", "semantic_duplicate_input"),
    )


def test_json_jsonl_and_csv_produce_equivalent_valid_reports(tmp_path) -> None:
    json_source = tmp_path / "dataset.json"
    jsonl_source = tmp_path / "dataset.jsonl"
    csv_source = tmp_path / "dataset.csv"
    records = [
        {
            "id": "case-001",
            "input": "texto",
            "expected_output": "A",
            "metadata": {"task": "classification", "label_set": ["A"], "partition": "test"},
        }
    ]
    json_source.write_text(json.dumps(records), encoding="utf-8")
    jsonl_source.write_text(json.dumps(records[0]) + "\n", encoding="utf-8")
    csv_source.write_text(
        "id,input,expected_output,metadata.task,metadata.label_set,metadata.partition\n"
        "case-001,texto,A,classification,A,test\n",
        encoding="utf-8",
    )

    reports = [
        DatasetValidator(_settings()).validate(load_dataset(source))
        for source in (json_source, jsonl_source, csv_source)
    ]

    assert [report.is_valid for report in reports] == [True, True, True]
    assert [report.summary.error_count for report in reports] == [0, 0, 0]


def test_jsonl_invalid_record_preserves_physical_line_and_aggregates(tmp_path) -> None:
    source = tmp_path / "dataset.jsonl"
    source.write_text(
        "\n"
        '{"id":"ok","input":"A","expected_output":"B","metadata":{"task":"classification","label_set":["B"],"partition":"train"}}\n'
        '{"id":"bad","input":"","expected_output":"B","metadata":{"task":"classification","partition":"test"}}\n',
        encoding="utf-8",
    )

    report = DatasetValidator(_settings()).validate(load_dataset(source))

    assert report.is_valid is False
    assert report.issues[0].location is not None
    assert report.issues[0].location.line == 3
    assert report.summary.issues_by_code == {"empty_input": 1, "missing_required_metadata": 1}
    assert report.summary.issues_by_task == {"classification": 2}
    assert report.summary.issues_by_partition == {"test": 2}


def test_rejects_invalid_jsonl_and_csv_mapping(tmp_path) -> None:
    bad_jsonl = tmp_path / "bad.jsonl"
    bad_jsonl.write_text('{"id":\n', encoding="utf-8")
    with pytest.raises(InvalidJsonError) as jsonl_error:
        load_dataset(bad_jsonl)
    assert "línea 1" in str(jsonl_error.value)

    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text("id,input\ncase,A\n", encoding="utf-8")
    with pytest.raises(InvalidDatasetError) as csv_error:
        load_dataset(bad_csv)
    assert "expected_output" in str(csv_error.value)


def test_csv_and_sarif_serializers_include_source_location(tmp_path) -> None:
    source = tmp_path / "dataset.jsonl"
    source.write_text('{"id":"bad","input":"","expected_output":"B","metadata":{}}\n', encoding="utf-8")
    report = DatasetValidator(
        ValidationSettings(disabled_rules=("empty_metadata", "semantic_duplicate_input"))
    ).validate(load_dataset(source))
    csv_report = tmp_path / "report.csv"
    sarif_report = tmp_path / "report.sarif"

    write_csv_report(report, csv_report)
    write_sarif_report(report, sarif_report)

    csv_rows = list(csv.DictReader(csv_report.read_text(encoding="utf-8").splitlines()))
    sarif = json.loads(sarif_report.read_text(encoding="utf-8"))
    assert csv_rows[0]["line"] == "1"
    assert sarif["version"] == "2.1.0"
    assert sarif["runs"][0]["results"][0]["locations"][0]["physicalLocation"]["region"]["startLine"] == 1


def test_cli_writes_json_csv_sarif_and_console_outputs(tmp_path, capsys) -> None:
    dataset = tmp_path / "dataset.jsonl"
    dataset.write_text('{"id":"bad","input":"","expected_output":"B","metadata":{}}\n', encoding="utf-8")
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"disabled_rules": ["empty_metadata", "semantic_duplicate_input"]}), encoding="utf-8")
    json_report = tmp_path / "report.json"
    csv_report = tmp_path / "report.csv"
    sarif_report = tmp_path / "report.sarif"

    exit_code = run(
        [
            str(dataset), "--config", str(config), "--report", str(json_report),
            "--output-format", "csv", "--output", str(csv_report),
        ]
    )
    sarif_exit_code = run(
        [
            str(dataset), "--config", str(config), "--report", str(json_report),
            "--output-format", "sarif", "--output", str(sarif_report),
        ]
    )
    console_exit_code = run(
        [str(dataset), "--config", str(config), "--report", str(json_report), "--output-format", "console"]
    )

    assert int(exit_code) == 1
    assert int(sarif_exit_code) == 1
    assert int(console_exit_code) == 1
    assert json_report.exists() and csv_report.exists() and sarif_report.exists()
    assert "Resumen:" in capsys.readouterr().out
