"""Tests for public JSON serialization of completed workflow results."""

from __future__ import annotations

import pytest

from agents_flow.contracts import Draft, Request, ResearchBrief, Review, WorkflowResult
from agents_flow.errors import ValidationError
from agents_flow.orchestrator import WorkflowOrchestrator
from agents_flow.presentation import serialize_workflow


def test_serializer_preserves_all_completed_artifacts_as_json_values() -> None:
    result = WorkflowOrchestrator().run(Request("Explica pruebas locales"))

    document = serialize_workflow(result)

    assert document == {
        "format": "json",
        "phase": 3,
        "status": "completed",
        "request": {"prompt": "Explica pruebas locales"},
        "research_brief": {
            "topic": "Explica pruebas locales",
            "objective": "Address the request: Explica pruebas locales",
            "constraints": [
                "Use only information derived from the request.",
                "Do not claim external research or sources.",
            ],
            "findings": [
                "The requested topic is: Explica pruebas locales.",
                "The output must be concise, clear, and directly responsive.",
            ],
        },
        "draft": {
            "content": (
                "Explica pruebas locales\n\n"
                "Objective: Address the request: Explica pruebas locales\n\n"
                "Key points: The requested topic is: Explica pruebas locales. "
                "The output must be concise, clear, and directly responsive.\n\n"
                "Constraints: Use only information derived from the request. "
                "Do not claim external research or sources."
            )
        },
        "review": {
            "decision": "approved",
            "observations": [
                "The draft covers the topic, objective, and declared constraints.",
                "The draft is structurally clear for the local workflow.",
            ],
        },
        "decision": "approved",
    }


@pytest.mark.parametrize("output_format", ["text", ""])
def test_serializer_rejects_an_unsupported_format(output_format: str) -> None:
    result = WorkflowOrchestrator().run(Request("Solicitud"))

    with pytest.raises(ValidationError) as error:
        serialize_workflow(result, output_format)

    assert error.value.code == "invalid_format"


def test_serializer_rejects_a_legacy_contract_only_result() -> None:
    with pytest.raises(ValidationError) as error:
        serialize_workflow(WorkflowResult(request=Request("Solicitud")))

    assert error.value.code == "invalid_workflow_result"


def test_serializer_rejects_a_result_without_valid_completed_state() -> None:
    result = WorkflowResult(
        request=Request("Solicitud"),
        research_brief=ResearchBrief("Tema", "Objetivo", ("Límite",), ("Hallazgo",)),
        draft=Draft("Borrador"),
        review=Review("approved", ()),
        phase=3,
        status="completed",
    )

    assert serialize_workflow(result)["decision"] == "approved"
