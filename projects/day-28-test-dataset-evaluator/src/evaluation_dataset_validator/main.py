"""Interfaz CLI local para validar datasets JSON, JSONL y CSV."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from evaluation_dataset_validator.config.loader import load_validation_settings
from evaluation_dataset_validator.errors import ApplicationError, ExitCode
from evaluation_dataset_validator.integrations import (
    LocalReportPublisher,
    WebhookReportPublisher,
    publish_with_fallback,
)
from evaluation_dataset_validator.reporting.formatters import (
    write_console_report,
    write_csv_report,
    write_sarif_report,
)
from evaluation_dataset_validator.reporting.json_report import write_json_report
from evaluation_dataset_validator.reporting.metrics import (
    write_json_metrics,
    write_prometheus_metrics,
)
from evaluation_dataset_validator.services.dataset_loader import SUPPORTED_INPUT_FORMATS, load_dataset
from evaluation_dataset_validator.validators.dataset import DatasetValidator


REPORT_FORMATS = ("json", "csv", "sarif", "console")
METRICS_FORMATS = ("json", "prometheus")


def build_parser() -> argparse.ArgumentParser:
    """Create the stable command-line interface for phase three."""
    parser = argparse.ArgumentParser(description="Valida datasets de evaluación locales.")
    parser.add_argument("dataset", type=Path, help="Ruta al archivo JSON, JSONL o CSV.")
    parser.add_argument(
        "--input-format",
        choices=("auto", *SUPPORTED_INPUT_FORMATS),
        default="auto",
        help="Formato de entrada; auto lo infiere por extensión (predeterminado: auto).",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/default.json"),
        help="Ruta al archivo JSON de configuración (predeterminado: config/default.json).",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("output/validation-report.json"),
        help="Ruta de salida para el informe JSON canónico.",
    )
    parser.add_argument(
        "--output-format",
        choices=REPORT_FORMATS,
        action="append",
        default=[],
        help="Salida adicional: console, csv o sarif. Se puede repetir; JSON siempre se escribe.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Ruta para la salida adicional cuando solo se pide un formato no JSON.",
    )
    parser.add_argument(
        "--metrics-format",
        choices=METRICS_FORMATS,
        action="append",
        default=[],
        help="Métrica adicional: json o prometheus. Se puede repetir.",
    )
    parser.add_argument(
        "--metrics-output",
        type=Path,
        help="Ruta para una métrica adicional; requiere exactamente un --metrics-format.",
    )
    parser.add_argument(
        "--publish-webhook",
        help="URL opcional para publicar métricas JSON tras validar; falla con fallback local.",
    )
    parser.add_argument(
        "--publish-fallback",
        type=Path,
        default=Path("output/integration-fallback.json"),
        help="Ruta local de fallback si falla --publish-webhook.",
    )
    return parser


def run(arguments: Sequence[str] | None = None) -> ExitCode:
    """Execute validation and return a documented process exit code."""
    parsed_arguments = build_parser().parse_args(arguments)
    try:
        _validate_output_arguments(parsed_arguments)
        settings = load_validation_settings(parsed_arguments.config)
        payload = load_dataset(parsed_arguments.dataset, parsed_arguments.input_format)
        report = DatasetValidator(settings=settings).validate(payload)
        write_json_report(report, parsed_arguments.report)
        _write_additional_reports(report, parsed_arguments)
        _write_metrics(report, parsed_arguments)
        _publish_optional_webhook(report, parsed_arguments)
    except ApplicationError as error:
        print(f"Error: {error}")
        return error.exit_code
    except OSError:
        print(f"Error: No se puede escribir el informe: {parsed_arguments.report}.")
        return ExitCode.FILE_ERROR

    print(f"Informe JSON guardado en {parsed_arguments.report}. Válido: {report.is_valid}.")
    if report.is_valid:
        return ExitCode.SUCCESS
    return ExitCode.VALIDATION_ERRORS


def _validate_output_arguments(arguments: argparse.Namespace) -> None:
    formats = tuple(dict.fromkeys(arguments.output_format))
    arguments.output_format = formats
    non_json_formats = tuple(output_format for output_format in formats if output_format != "json")
    if arguments.output is not None and len(non_json_formats) != 1:
        raise ApplicationError(
            "--output requiere exactamente un --output-format adicional distinto de json.",
            ExitCode.INVALID_INPUT,
        )
    metrics_formats = tuple(dict.fromkeys(arguments.metrics_format))
    arguments.metrics_format = metrics_formats
    if arguments.metrics_output is not None and len(metrics_formats) != 1:
        raise ApplicationError(
            "--metrics-output requiere exactamente un --metrics-format.",
            ExitCode.INVALID_INPUT,
        )


def _write_additional_reports(report, arguments: argparse.Namespace) -> None:
    for output_format in arguments.output_format:
        if output_format == "json":
            continue
        if output_format == "console":
            write_console_report(report, sys.stdout)
            continue
        destination = arguments.output or arguments.report.with_suffix(
            ".csv" if output_format == "csv" else ".sarif"
        )
        if output_format == "csv":
            write_csv_report(report, destination)
        elif output_format == "sarif":
            write_sarif_report(report, destination)


def _write_metrics(report, arguments: argparse.Namespace) -> None:
    for metrics_format in arguments.metrics_format:
        destination = arguments.metrics_output or arguments.report.with_suffix(
            ".metrics.json" if metrics_format == "json" else ".prom"
        )
        if metrics_format == "json":
            write_json_metrics(report, destination)
        else:
            write_prometheus_metrics(report, destination)


def _publish_optional_webhook(report, arguments: argparse.Namespace) -> None:
    if not arguments.publish_webhook:
        return
    result = publish_with_fallback(
        report,
        WebhookReportPublisher(arguments.publish_webhook),
        LocalReportPublisher(arguments.publish_fallback),
    )
    if result == "fallback":
        print(f"Integración webhook no disponible; fallback local guardado en {arguments.publish_fallback}.")
    else:
        print("Métricas publicadas en el webhook.")


def main() -> None:
    """Run the installed CLI command with the process' original arguments."""
    raise SystemExit(run())


if __name__ == "__main__":
    main()
