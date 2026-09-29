"""Pruebas de integración para la API local v1."""

from fastapi.testclient import TestClient

from src.domain.contracts import HealthDashboardFixture
from src.main import create_app
from src.repositories.local_fixture_repository import DashboardDataError, LocalFixtureDashboardRepository


class EmptyDashboardRepository:
    """Doble local con el contrato válido y ninguna medición."""

    def __init__(self, delegate: LocalFixtureDashboardRepository) -> None:
        self._delegate = delegate

    def load_dashboard(self) -> HealthDashboardFixture:
        dashboard = self._delegate.load_dashboard()
        return dashboard.model_copy(update={"measurements": []}, deep=True)


class FailingDashboardRepository:
    """Doble que simula un fallo de lectura sin revelar su causa."""

    def load_dashboard(self) -> HealthDashboardFixture:
        raise DashboardDataError("fixture parse error")


def create_client() -> TestClient:
    """Aísla la sesión de repositorio en memoria de cada caso de prueba."""
    return TestClient(create_app())


def test_get_dashboard_returns_the_v1_fixture() -> None:
    client = create_client()

    response = client.get("/api/v1/dashboard")

    assert response.status_code == 200
    body = response.json()
    assert body["metadata"]["contractVersion"] == "v1"
    assert body["metadata"]["source"] == "synthetic-fixture"
    assert body["measurements"]


def test_get_dashboard_can_return_an_empty_measurement_collection() -> None:
    application = create_app()
    application.state.dashboard_repository = EmptyDashboardRepository(application.state.dashboard_repository)
    client = TestClient(application)

    response = client.get("/api/v1/dashboard")

    assert response.status_code == 200
    assert response.json()["measurements"] == []


def test_create_measurement_adds_a_manual_value_to_the_local_session() -> None:
    client = create_client()
    payload = {
        "metricId": "daily-steps",
        "value": 1200,
        "recordedAt": "2026-09-02T08:00:00Z",
    }

    response = client.post("/api/v1/measurements", json=payload)

    assert response.status_code == 201
    assert response.json() == {
        "id": "manual-measurement-4",
        **payload,
        "source": "manual",
    }


def test_created_manual_measurement_is_available_in_the_same_dashboard_session() -> None:
    client = create_client()
    payload = {
        "metricId": "water-intake",
        "value": 350,
        "recordedAt": "2026-09-02T09:00:00Z",
    }

    created = client.post("/api/v1/measurements", json=payload)
    dashboard = client.get("/api/v1/dashboard")

    assert created.status_code == 201
    assert dashboard.status_code == 200
    assert dashboard.json()["measurements"][-1] == created.json()


def test_create_measurement_rejects_invalid_payload_without_echoing_values() -> None:
    client = create_client()

    response = client.post(
        "/api/v1/measurements",
        json={
            "metricId": "daily-steps",
            "value": "not-a-number",
            "recordedAt": "not-a-date",
        },
    )

    assert response.status_code == 422
    assert response.json() == {
        "code": "invalid_request",
        "message": "La solicitud no cumple el formato requerido.",
        "details": ["datetime_from_date_parsing", "float_parsing"],
    }
    assert "not-a-number" not in response.text


def test_create_measurement_returns_not_found_for_an_unknown_metric() -> None:
    client = create_client()

    response = client.post(
        "/api/v1/measurements",
        json={
            "metricId": "unknown-metric",
            "value": 1,
            "recordedAt": "2026-09-02T08:00:00Z",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "code": "metric_not_found",
        "message": "La métrica solicitada no está disponible.",
        "details": [],
    }


def test_dashboard_source_failure_returns_a_safe_error() -> None:
    application = create_app()
    application.state.dashboard_repository = FailingDashboardRepository()
    client = TestClient(application)

    response = client.get("/api/v1/dashboard")

    assert response.status_code == 503
    assert response.json() == {
        "code": "dashboard_unavailable",
        "message": "La fuente local del dashboard no está disponible.",
        "details": [],
    }
    assert "parse error" not in response.text


def test_cors_allows_only_the_configured_local_origin() -> None:
    client = create_client()

    response = client.options(
        "/api/v1/dashboard",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
