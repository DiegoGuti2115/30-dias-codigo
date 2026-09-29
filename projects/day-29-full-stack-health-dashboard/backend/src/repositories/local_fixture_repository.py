"""Adaptador local que lee el fixture sintético versionado."""

import json
from pathlib import Path

from pydantic import ValidationError

from src.domain.contracts import HealthDashboardFixture, Measurement, MeasurementCreate, MeasurementSource


class DashboardDataError(Exception):
    """Indica que la fuente local no puede proporcionar un dashboard válido."""


class LocalFixtureDashboardRepository:
    """Repositorio en memoria inicializado desde un fixture local validado."""

    def __init__(self, fixture_path: Path) -> None:
        self._fixture_path = fixture_path
        self._dashboard: HealthDashboardFixture | None = None

    def load_dashboard(self) -> HealthDashboardFixture:
        """Carga y valida el fixture una vez; no realiza llamadas de red."""
        if self._dashboard is None:
            try:
                raw_dashboard = json.loads(self._fixture_path.read_text(encoding="utf-8"))
                self._dashboard = HealthDashboardFixture.model_validate(raw_dashboard)
                self._validate_references(self._dashboard)
            except (OSError, json.JSONDecodeError, ValidationError, ValueError) as error:
                raise DashboardDataError("The local dashboard source is unavailable") from error
        return self._dashboard.model_copy(deep=True)

    def add_manual_measurement(self, measurement: MeasurementCreate) -> Measurement:
        """Añade una medición manual únicamente a la sesión de la demo local."""
        dashboard = self.load_dashboard()
        metric_ids = {metric.id for metric in dashboard.metrics}
        if measurement.metricId not in metric_ids:
            raise KeyError("Unknown metric")

        next_measurement = Measurement(
            id=self._next_measurement_id(dashboard),
            metricId=measurement.metricId,
            value=measurement.value,
            recordedAt=measurement.recordedAt,
            source=MeasurementSource.MANUAL,
        )
        self._dashboard = dashboard.model_copy(
            update={"measurements": [*dashboard.measurements, next_measurement]},
            deep=True,
        )
        return next_measurement

    @staticmethod
    def _validate_references(dashboard: HealthDashboardFixture) -> None:
        metric_ids = {metric.id for metric in dashboard.metrics}
        if len(metric_ids) != len(dashboard.metrics):
            raise ValueError("Metric identifiers must be unique")
        if len({measurement.id for measurement in dashboard.measurements}) != len(
            dashboard.measurements
        ):
            raise ValueError("Measurement identifiers must be unique")
        if any(measurement.metricId not in metric_ids for measurement in dashboard.measurements):
            raise ValueError("Measurement references an unknown metric")

    @staticmethod
    def _next_measurement_id(dashboard: HealthDashboardFixture) -> str:
        index = len(dashboard.measurements) + 1
        while True:
            candidate = f"manual-measurement-{index}"
            if all(measurement.id != candidate for measurement in dashboard.measurements):
                return candidate
            index += 1
