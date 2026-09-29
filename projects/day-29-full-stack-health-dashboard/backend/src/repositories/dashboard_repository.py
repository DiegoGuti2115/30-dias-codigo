"""Puerto de datos para fuentes locales o persistentes del dashboard."""

from typing import Protocol

from src.domain.contracts import HealthDashboardFixture, Measurement, MeasurementCreate


class DashboardRepository(Protocol):
    """Obtiene y registra datos no clínicos sin exponer un proveedor concreto."""

    def load_dashboard(self) -> HealthDashboardFixture:
        """Devuelve el dashboard completo desde la fuente configurada."""

    def add_manual_measurement(self, measurement: MeasurementCreate) -> Measurement:
        """Registra una medición manual en la fuente disponible."""
