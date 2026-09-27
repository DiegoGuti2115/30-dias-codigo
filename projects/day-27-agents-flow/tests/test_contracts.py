"""Pruebas de los contratos públicos de la Fase 1."""

from __future__ import annotations

import pytest

from agents_flow.contracts import (
    ORCHESTRATION_PHASE,
    PHASE,
    STATUS_COMPLETED,
    STATUS_CONTRACT_ONLY,
    Draft,
    Request,
    ResearchBrief,
    Review,
    WorkflowResult,
)
from agents_flow.errors import ValidationError


def test_request_preserves_a_valid_prompt_without_normalizing_it() -> None:
    request = Request("  Escribe una guía breve  ")

    assert request.prompt == "  Escribe una guía breve  "


@pytest.mark.parametrize(
    ("prompt", "code"),
    [
        ("", "invalid_prompt"),
        ("   ", "invalid_prompt"),
        (None, "invalid_prompt_type"),
        (42, "invalid_prompt_type"),
    ],
)
def test_request_rejects_invalid_prompts(prompt: object, code: str) -> None:
    with pytest.raises(ValidationError) as error:
        Request(prompt)  # type: ignore[arg-type]

    assert error.value.code == code


def test_reserved_artifact_contracts_are_immutable_and_typed() -> None:
    research = ResearchBrief(
        topic="Pruebas", objective="Explicar", constraints=("breve",), findings=("local",)
    )
    draft = Draft(content="Borrador")
    review = Review(decision="approved", observations=())

    assert research.topic == "Pruebas"
    assert draft.content == "Borrador"
    assert review.decision == "approved"
    with pytest.raises(AttributeError):
        draft.content = "Otro"  # type: ignore[misc]


def test_workflow_result_exposes_the_phase_one_contract() -> None:
    result = WorkflowResult(request=Request("Documenta el contrato"))

    assert result.phase == PHASE
    assert result.status == STATUS_CONTRACT_ONLY
    assert result.request.prompt == "Documenta el contrato"


def test_workflow_result_exposes_completed_orchestration_artifacts() -> None:
    request = Request("Documenta el flujo")
    brief = ResearchBrief("Flujo", "Documentar", ("Sin red",), ("Local",))
    draft = Draft("Flujo\nDocumentar\nSin red")
    review = Review("approved", ("Cubierto",))

    result = WorkflowResult(
        request=request,
        research_brief=brief,
        draft=draft,
        review=review,
        phase=ORCHESTRATION_PHASE,
        status=STATUS_COMPLETED,
    )

    assert result.research_brief is brief
    assert result.draft is draft
    assert result.review is review


def test_completed_workflow_result_requires_every_role_artifact() -> None:
    with pytest.raises(ValidationError) as error:
        WorkflowResult(
            request=Request("Solicitud"),
            phase=ORCHESTRATION_PHASE,
            status=STATUS_COMPLETED,
        )

    assert error.value.code == "invalid_research_brief"


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("phase", 2, "invalid_phase"),
        ("status", "completed", "invalid_status"),
    ],
)
def test_workflow_result_rejects_values_outside_phase_one(
    field: str, value: object, code: str
) -> None:
    values = {"request": Request("Solicitud válida"), field: value}

    with pytest.raises(ValidationError) as error:
        WorkflowResult(**values)  # type: ignore[arg-type]

    assert error.value.code == code
