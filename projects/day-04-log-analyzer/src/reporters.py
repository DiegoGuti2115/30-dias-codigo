"""Deterministic terminal-oriented renderers for phase 4 analysis results."""

from __future__ import annotations

from os import PathLike

from analyzer import AnalysisResult


def format_summary(result: AnalysisResult, source_path: str | PathLike[str]) -> str:
    """Render the complete v1 summary without recalculating any metric."""

    lines = [
        "Resumen de análisis",
        f"Ruta: {source_path}",
        f"Formato: {result.log_format}",
        f"Líneas leídas: {result.total_lines}",
        f"Eventos válidos: {result.valid_events}",
        f"Líneas inválidas: {result.invalid_lines}",
        "Por nivel:",
    ]
    lines.extend(f"- {level}: {count}" for level, count in result.level_counts)
    lines.append("Mensajes frecuentes:")

    if result.top_messages:
        lines.extend(
            f"- {item.count} × {item.message}" for item in result.top_messages
        )
    else:
        lines.append("- Sin eventos válidos.")

    return "\n".join(lines)


def format_error_report(result: AnalysisResult) -> str:
    """Render selected ERROR/CRITICAL events in their original physical order."""

    if not result.error_events:
        return "Reporte de errores\nSin eventos ERROR o CRITICAL."

    lines = ["Reporte de errores"]
    lines.extend(
        "- línea {line} | {timestamp} | {level} | {message}".format(
            line=event.line_number,
            timestamp=event.timestamp,
            level=event.level,
            message=event.message,
        )
        for event in result.error_events
    )
    return "\n".join(lines)


def format_analysis(result: AnalysisResult, source_path: str | PathLike[str], *, include_errors: bool = False) -> str:
    """Render a summary and, when requested, the fixed-threshold error report."""

    summary = format_summary(result, source_path)
    return f"{summary}\n\n{format_error_report(result)}" if include_errors else summary
