"""Pruebas de automatización, observabilidad e integraciones opcionales de fase cinco."""

from __future__ import annotations

import json

from evaluation_dataset_validator.integrations import LocalReportPublisher, publish_with_fallback
from evaluation_dataset_validator.main import run
from evaluation_dataset_validator.models.contracts import (
    Severity,
    ValidationIssue,
    ValidationReport,
    ValidationSummary,
)
from evaluation_dataset_validator.reporting.metrics import (
    metrics_payload,
    write_json_metrics,
    write_prometheus_metrics,
)


def _report() -> ValidationReport:
    return ValidationReport(
        is_valid=False,
        summary=ValidationSummary(
            total_records=2,
            valid_records=1,
            error_count=1,
            warning_count=1,
            issues_by_code={"invalid_schema": 1, "missing_coverage": 1},
            issues_by_task={"classification": 1},
            issues_by_partition={"test": 2},
            coverage_by_field={"metadata.language": {"en": 1, "es": 1}},
        ),
        issues=[ValidationIssue(code="invalid_schema", message="Esquema inválido.", severity=Severity.ERROR, rule="schema")],
    )


def test_metrics_json_and_prometheus_are_deterministic_and_parseable(tmp_path) -> None:
    report = _report()
    json_destination = tmp_path / "metrics.json"
    prometheus_destination = tmp_path / "metrics.prom"

    write_json_metrics(report, json_destination)
    write_prometheus_metrics(report, prometheus_destination)

    assert json.loads(json_destination.read_text(encoding="utf-8")) == metrics_payload(report)
    prometheus = prometheus_destination.read_text(encoding="utf-8")
    assert 'evaluation_dataset_valid 0' in prometheus
    assert 'evaluation_dataset_issues_by_code{code="invalid_schema"} 1' in prometheus
    assert 'evaluation_dataset_coverage{field="metadata.language",value="es"} 1' in prometheus


def test_failed_optional_publisher_uses_local_fallback_without_affecting_report(tmp_path) -> None:
    class FailingPublisher:
        def publish(self, report: ValidationReport) -> None:
            raise OSError("sin conexión")

    fallback = tmp_path / "fallback.json"
    result = publish_with_fallback(_report(), FailingPublisher(), LocalReportPublisher(fallback))

    assert result == "fallback"
    assert json.loads(fallback.read_text(encoding="utf-8"))["error_count"] == 1


def test_cli_writes_metrics_and_webhook_fallback_but_keeps_success_exit(tmp_path, capsys) -> None:
    dataset = tmp_path / "dataset.json"
    dataset.write_text('[{"id":"ok","input":"A","expected_output":"B","metadata":{}}]', encoding="utf-8")
    config = tmp_path / "config.json"
    config.write_text('{"warn_on_empty_metadata": false, "detect_semantic_duplicates": false}', encoding="utf-8")
    report = tmp_path / "report.json"
    metrics = tmp_path / "metrics.prom"
    fallback = tmp_path / "fallback.json"

    exit_code = run([
        str(dataset), "--config", str(config), "--report", str(report),
        "--metrics-format", "prometheus", "--metrics-output", str(metrics),
        "--publish-webhook", "http://127.0.0.1:1/unavailable", "--publish-fallback", str(fallback),
    ])

    assert int(exit_code) == 0
    assert metrics.exists() and fallback.exists()
    assert "fallback local" in capsys.readouterr().out


def test_cli_rejects_ambiguous_metrics_destination(tmp_path, capsys) -> None:
    dataset = tmp_path / "dataset.json"
    dataset.write_text("[]", encoding="utf-8")

    exit_code = run([str(dataset), "--metrics-output", str(tmp_path / "metrics.json")])

    assert int(exit_code) == 2
    assert "--metrics-output requiere" in capsys.readouterr().out
