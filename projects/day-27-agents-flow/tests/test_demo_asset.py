"""Regression tests for the reproducible Phase 7 demonstration resource."""

from __future__ import annotations

import json
from pathlib import Path

from agents_flow.main import main

DEMO_PATH = Path(__file__).parents[1] / "assets" / "demo-15s.md"


def test_demo_script_documents_the_local_command_and_traceable_result() -> None:
    content = DEMO_PATH.read_text(encoding="utf-8")

    assert "# Demo local — 15 segundos" in content
    assert 'python -m agents_flow.main "Explica la trazabilidad del café local."' in content
    assert "research_brief" in content
    assert "draft" in content
    assert "review" in content
    assert '"decision": "approved"' in content
    assert "No requiere red, credenciales, proveedor LLM" in content


def test_demo_command_remains_compatible_with_the_approved_fixture(capsys) -> None:
    exit_code = main(["Explica la trazabilidad del café local."])

    document = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert document["request"]["prompt"] == "Explica la trazabilidad del café local."
    assert document["decision"] == "approved"
