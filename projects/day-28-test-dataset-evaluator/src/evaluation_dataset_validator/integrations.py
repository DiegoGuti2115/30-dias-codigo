"""Adaptadores opcionales con fallback local garantizado."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
from urllib.error import URLError
from urllib.request import Request, urlopen

from evaluation_dataset_validator.models.contracts import ValidationReport
from evaluation_dataset_validator.reporting.metrics import metrics_payload


class ReportPublisher(Protocol):
    """Optional destination for a validation report; implementations must be side-effect isolated."""

    def publish(self, report: ValidationReport) -> None:
        """Publish a report or raise an infrastructure error."""


@dataclass(frozen=True, slots=True)
class LocalReportPublisher:
    """Deterministic fallback that persists an integration payload locally."""

    destination: Path

    def publish(self, report: ValidationReport) -> None:
        self.destination.parent.mkdir(parents=True, exist_ok=True)
        self.destination.write_text(
            json.dumps(metrics_payload(report), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


@dataclass(frozen=True, slots=True)
class WebhookReportPublisher:
    """Minimal optional webhook adapter with no dependency or credential requirement."""

    endpoint: str
    timeout_seconds: float = 3.0

    def publish(self, report: ValidationReport) -> None:
        payload = json.dumps(metrics_payload(report), ensure_ascii=False).encode("utf-8")
        request = Request(
            self.endpoint,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                if response.status < 200 or response.status >= 300:
                    raise OSError(f"el webhook respondió con estado HTTP {response.status}")
        except (URLError, TimeoutError, ValueError) as error:
            detail = getattr(error, "reason", str(error))
            raise OSError(f"no se pudo publicar en el webhook: {detail}") from error


def publish_with_fallback(
    report: ValidationReport, publisher: ReportPublisher, fallback: LocalReportPublisher
) -> str:
    """Attempt an optional integration and always persist a local fallback on failure."""
    try:
        publisher.publish(report)
    except OSError:
        fallback.publish(report)
        return "fallback"
    return "remote"
