"""Tests for deterministic, isolated local agent adapters from Phase 2."""

from __future__ import annotations

import pytest

from agents_flow.agents import LocalResearcher, LocalReviewer, LocalWriter
from agents_flow.contracts import Draft, Request, ResearchBrief, Review
from agents_flow.errors import ValidationError


def test_local_roles_produce_the_same_valid_artifacts_for_the_same_request() -> None:
    request = Request("Explica pruebas automatizadas para una API pequeña")
    researcher = LocalResearcher()
    writer = LocalWriter()
    reviewer = LocalReviewer()

    first_brief = researcher.research(request)
    first_draft = writer.write(first_brief)
    first_review = reviewer.review(first_brief, first_draft)
    second_brief = researcher.research(request)
    second_draft = writer.write(second_brief)
    second_review = reviewer.review(second_brief, second_draft)

    assert first_brief == second_brief
    assert first_draft == second_draft
    assert first_review == second_review
    assert first_review.decision == "approved"
    assert "external research" in first_brief.constraints[1]


def test_writer_uses_only_the_research_brief_contract() -> None:
    brief = ResearchBrief(
        topic="Pruebas locales",
        objective="Explicar el flujo",
        constraints=("No usar red.", "Mantener determinismo."),
        findings=("El flujo usa contratos.",),
    )

    draft = LocalWriter().write(brief)

    assert "Pruebas locales" in draft.content
    assert "Explicar el flujo" in draft.content
    assert "No usar red." in draft.content
    assert "El flujo usa contratos." in draft.content


def test_reviewer_requests_changes_when_a_required_brief_element_is_missing() -> None:
    brief = ResearchBrief(
        topic="Tema necesario",
        objective="Objetivo necesario",
        constraints=("Restricción necesaria",),
        findings=("Hallazgo local",),
    )

    review = LocalReviewer().review(brief, Draft("Tema necesario"))

    assert review.decision == "changes_requested"
    assert review.observations == (
        "Missing required coverage: Objetivo necesario",
        "Missing required coverage: Restricción necesaria",
    )


@pytest.mark.parametrize(
    ("factory", "code"),
    [
        (
            lambda: ResearchBrief("", "Objetivo", ("Límite",), ("Hallazgo",)),
            "invalid_topic",
        ),
        (
            lambda: ResearchBrief("Tema", "Objetivo", (), ("Hallazgo",)),
            "invalid_constraints",
        ),
        (lambda: Draft("   "), "invalid_content"),
        (lambda: Review("deferred", ()), "invalid_decision"),
        (lambda: Review("changes_requested", ()), "invalid_observations"),
    ],
)
def test_phase_two_artifacts_reject_invalid_semantic_values(factory, code: str) -> None:
    with pytest.raises(ValidationError) as error:
        factory()

    assert error.value.code == code
