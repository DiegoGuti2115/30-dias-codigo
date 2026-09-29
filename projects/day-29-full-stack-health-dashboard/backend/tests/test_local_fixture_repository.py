"""Pruebas unitarias del adaptador de fixture local."""

import json
from pathlib import Path

import pytest

from src.domain.contracts import MeasurementCreate
from src.repositories.local_fixture_repository import DashboardDataError, LocalFixtureDashboardRepository


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = PROJECT_ROOT / "data" / "fixtures" / "health-dashboard.sample.json"


def test_repository_loads_a_valid_local_fixture() -> None:
    repository = LocalFixtureDashboardRepository(FIXTURE_PATH)

    dashboard = repository.load_dashboard()

    assert dashboard.metadata.contractVersion == "v1"
    assert dashboard.metrics


def test_repository_rejects_an_invalid_measurement_reference(tmp_path: Path) -> None:
    invalid_fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    invalid_fixture["measurements"][0]["metricId"] = "unknown-metric"
    fixture_path = tmp_path / "invalid-dashboard.json"
    fixture_path.write_text(json.dumps(invalid_fixture), encoding="utf-8")
    repository = LocalFixtureDashboardRepository(fixture_path)

    with pytest.raises(DashboardDataError):
        repository.load_dashboard()


def test_repository_rejects_an_unknown_metric_when_adding_a_measurement() -> None:
    repository = LocalFixtureDashboardRepository(FIXTURE_PATH)
    payload = MeasurementCreate(
        metricId="unknown-metric",
        value=1,
        recordedAt="2026-09-02T08:00:00Z",
    )

    with pytest.raises(KeyError):
        repository.add_manual_measurement(payload)


def test_repository_assigns_unique_manual_identifiers() -> None:
    repository = LocalFixtureDashboardRepository(FIXTURE_PATH)
    payload = MeasurementCreate(
        metricId="daily-steps",
        value=1,
        recordedAt="2026-09-02T08:00:00Z",
    )

    first = repository.add_manual_measurement(payload)
    second = repository.add_manual_measurement(payload)

    assert first.id == "manual-measurement-4"
    assert second.id == "manual-measurement-5"
    assert first.source == "manual"
