"""Regression coverage for the versioned Phase 8 delivery resources."""

from __future__ import annotations

from pathlib import Path

ASSETS_DIRECTORY = Path(__file__).parents[1] / "assets"
FINAL_DELIVERY_PATH = ASSETS_DIRECTORY / "final-delivery.md"
LINKEDIN_POST_PATH = ASSETS_DIRECTORY / "linkedin-post.md"


def test_final_delivery_evidence_documents_reproducible_closure_checks() -> None:
    content = FINAL_DELIVERY_PATH.read_text(encoding="utf-8")

    assert "# Cierre verificable — Flujo de agentes" in content
    assert "python -m pytest -q" in content
    assert "python -m compileall -q src" in content
    assert "python -m agents_flow.main --help" in content
    assert 'python -m agents_flow.main "Explica la trazabilidad del café local."' in content
    assert "git diff --check" in content
    assert '"phase": 3' in content
    assert '"status": "completed"' in content
    assert '"decision": "approved"' in content
    assert "data/workflow_cases.json" in content
    assert "assets/demo-15s.md" in content


def test_linkedin_copy_describes_only_verified_local_capabilities() -> None:
    content = LINKEDIN_POST_PATH.read_text(encoding="utf-8")

    assert "# Copy para LinkedIn — Día 27: Flujo de agentes" in content
    assert "30 Días, 30 Proyectos" in content
    assert "Python" in content
    assert "JSON UTF-8" in content
    assert "sin red, secretos ni servicios externos" in content
    assert "Microsoft Foundry se evaluó, pero se descartó" in content
    assert "assets/demo-15s.md" in content
    assert "assets/final-delivery.md" in content
    assert "No afirmar:" in content
