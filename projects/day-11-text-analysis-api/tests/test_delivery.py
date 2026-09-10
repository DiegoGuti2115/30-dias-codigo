"""Delivery-documentation regression tests for Phase 7."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_delivery_guide_documents_verified_local_workflow() -> None:
    guide = (PROJECT_ROOT / "docs" / "GUIA_DE_ENTREGA.md").read_text(encoding="utf-8")

    assert "# Guía de entrega — API de análisis de texto" in guide
    assert "python -m uvicorn src.main:app --reload" in guide
    assert ".\\.venv\\Scripts\\python.exe -m pytest -q" in guide
    assert "http://127.0.0.1:8000/docs" in guide
    assert "No use datos personales, confidenciales o de producción" in guide


def test_demo_references_the_versioned_fixture_and_expected_result() -> None:
    demo = (PROJECT_ROOT / "assets" / "DEMO_HTTP.md").read_text(encoding="utf-8")

    assert "http://127.0.0.1:8000/api/v1/analyze" in demo
    assert "../data/fixtures/contract-example.txt" in demo
    assert "../data/expected/contract-example.json" in demo
    assert '"character_count": 54' in demo


def test_delivery_references_are_present_in_the_project() -> None:
    references = [
        "README.md",
        "ROADMAP.md",
        "docs/CONTRATO_API_V1.md",
        "docs/GUIA_DE_ENTREGA.md",
        "assets/DEMO_HTTP.md",
        "assets/carrusel-linkedin.html",
        "data/fixtures/contract-example.txt",
        "data/expected/contract-example.json",
    ]

    assert all((PROJECT_ROOT / reference).is_file() for reference in references)


def test_linkedin_carousel_presents_the_verified_v1_evidence() -> None:
    carousel = (PROJECT_ROOT / "assets" / "carrusel-linkedin.html").read_text(
        encoding="utf-8"
    )

    assert "API de análisis de texto: de un texto a métricas reproducibles" in carousel
    assert "Python + FastAPI + Pydantic" in carousel
    assert "POST /api/v1/analyze" in carousel
    assert "50</b>" in carousel
    assert "fixture versionado" in carousel
    assert "Repositorio en el primer comentario / enlace" in carousel
    assert "prefers-reduced-motion" in carousel
    assert "aria-live" in carousel
    assert "touchstart" in carousel
