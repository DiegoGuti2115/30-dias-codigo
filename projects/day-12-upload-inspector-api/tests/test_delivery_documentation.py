"""Regression checks for the verified Phase 7 delivery documentation."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _read_project_file(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_delivery_guide_documents_the_existing_local_v1_contract() -> None:
    guide = _read_project_file("docs/GUIA_DE_ENTREGA.md")

    assert "POST /api/v1/inspect" in guide
    assert "multipart `file`" in guide
    assert "5.242.881" in guide
    assert "file_too_large" in guide
    assert "malformed_multipart" in guide
    assert "unsupported_media_type" in guide
    assert "Azure Blob" in guide
    assert "No persiste archivos, resultados ni metadatos." in guide


def test_delivery_guide_uses_the_safe_versioned_fixture_and_expected_result() -> None:
    guide = _read_project_file("docs/GUIA_DE_ENTREGA.md")

    assert "phase-4-sample.txt" in guide
    assert "phase-4-sample.json" in guide
    assert "2d1defc09b2948c1d59fde60b0fedd4c0155f8d28e954ab3c9dd28e2e64ab167" in guide
    assert "curl.exe" in guide
    assert "127.0.0.1" in guide


def test_readme_links_the_delivery_guide_and_reports_verified_v1_status() -> None:
    readme = _read_project_file("README.md")

    assert "versión 1 local, sin estado y sin persistencia completada y verificada" in readme
    assert "[docs/GUIA_DE_ENTREGA.md](docs/GUIA_DE_ENTREGA.md)" in readme


def test_linkedin_copy_and_carousel_stay_within_the_verified_v1_scope() -> None:
    publication = _read_project_file("docs/LINKEDIN_DIA_12.md")
    carousel = _read_project_file("assets/carrusel-linkedin.html")

    assert "sin almacenarlo" in publication
    assert "exactamente un archivo" in publication
    assert "5 MiB" in publication
    assert "no detecta malware" in publication
    assert "#30Dias30Proyectos" in publication
    assert "POST /api/v1/inspect" in carousel
    assert "5 MiB" in carousel
    assert "no detecta malware" in carousel
    assert "Azure Blob en la versión 1" in carousel


def test_linkedin_carousel_provides_accessible_client_side_navigation() -> None:
    carousel = _read_project_file("assets/carrusel-linkedin.html")

    assert carousel.count('class="slide') == 8
    assert 'aria-roledescription="carrusel"' in carousel
    assert 'aria-label="Ver diapositiva anterior"' in carousel
    assert 'aria-label="Ver diapositiva siguiente"' in carousel
    assert 'aria-selected' in carousel
    assert "ArrowLeft" in carousel
    assert "ArrowRight" in carousel
    assert "touchstart" in carousel
    assert "touchend" in carousel
    assert "prefers-reduced-motion" in carousel
