"""Pruebas del contrato v1 y del fixture sintético compartido."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.domain.contracts import HealthDashboardFixture

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = PROJECT_ROOT / "data" / "fixtures" / "health-dashboard.sample.json"
SCHEMA_PATH = PROJECT_ROOT / "shared" / "contracts" / "v1" / "dashboard.schema.json"


def load_fixture() -> dict[str, object]:
    """Carga el fixture que utilizarán las capas futuras."""
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_fixture_matches_pydantic_contract_v1() -> None:
    """El fixture se valida con el modelo sincronizado con el esquema JSON."""
    dashboard = HealthDashboardFixture.model_validate(load_fixture())

    assert dashboard.metadata.contractVersion == "v1"
    assert dashboard.metadata.source == "synthetic-fixture"
    assert dashboard.metrics


def test_fixture_measurements_reference_defined_metrics() -> None:
    """Cada medición debe referenciar una métrica declarada en el mismo contrato."""
    dashboard = HealthDashboardFixture.model_validate(load_fixture())
    metric_ids = {metric.id for metric in dashboard.metrics}

    assert {measurement.metricId for measurement in dashboard.measurements} <= metric_ids


def test_fixture_identifiers_are_unique_per_resource() -> None:
    """Evita ambigüedad antes de que exista persistencia."""
    dashboard = HealthDashboardFixture.model_validate(load_fixture())

    assert len({metric.id for metric in dashboard.metrics}) == len(dashboard.metrics)
    assert len({measurement.id for measurement in dashboard.measurements}) == len(
        dashboard.measurements
    )


def test_schema_declares_v1_and_non_clinical_contract() -> None:
    """El esquema versionado preserva la restricción no clínica del contrato."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    assert schema["$id"].endswith("/v1/dashboard.schema.json")
    assert "No define rangos" in schema["description"]
    assert schema["properties"]["metadata"]["properties"]["contractVersion"] == {
        "const": "v1"
    }


def test_contract_rejects_unknown_properties() -> None:
    """Evita que campos no versionados se filtren entre capas."""
    fixture = load_fixture()
    fixture["unexpected"] = "value"

    with pytest.raises(ValidationError):
        HealthDashboardFixture.model_validate(fixture)
