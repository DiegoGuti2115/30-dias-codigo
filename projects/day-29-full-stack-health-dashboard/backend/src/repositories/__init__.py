"""Puertos de persistencia independientes de proveedores."""

from .dashboard_repository import DashboardRepository
from .local_fixture_repository import DashboardDataError, LocalFixtureDashboardRepository

__all__ = ["DashboardDataError", "DashboardRepository", "LocalFixtureDashboardRepository"]
