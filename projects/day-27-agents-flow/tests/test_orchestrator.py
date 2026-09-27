"""Behavioral tests for the Phase 3 workflow orchestration use case."""

from __future__ import annotations

import pytest

from agents_flow.contracts import (
    ORCHESTRATION_PHASE,
    STATUS_COMPLETED,
    Draft,
    Request,
    ResearchBrief,
    Review,
)
from agents_flow.errors import StageError, ValidationError
from agents_flow.orchestrator import WorkflowOrchestrator


class RecordingResearcher:
    def __init__(self, events: list[str], brief: ResearchBrief) -> None:
        self.events = events
        self.brief = brief

    def research(self, request: Request) -> ResearchBrief:
        self.events.append(f"research:{request.prompt}")
        return self.brief


class RecordingWriter:
    def __init__(self, events: list[str], draft: Draft) -> None:
        self.events = events
        self.draft = draft
        self.received_brief: ResearchBrief | None = None

    def write(self, brief: ResearchBrief) -> Draft:
        self.events.append("writing")
        self.received_brief = brief
        return self.draft


class RecordingReviewer:
    def __init__(self, events: list[str], result: Review) -> None:
        self.events = events
        self.result = result
        self.received: tuple[ResearchBrief, Draft] | None = None

    def review(self, brief: ResearchBrief, draft: Draft) -> Review:
        self.events.append("review")
        self.received = (brief, draft)
        return self.result


class FailingResearcher:
    def research(self, request: Request) -> ResearchBrief:
        raise ValidationError("invalid_research", "research input cannot be used")


class UnreachableWriter:
    def write(self, brief: ResearchBrief) -> Draft:
        raise AssertionError("writer must not run after a failed research stage")


class UnreachableReviewer:
    def review(self, brief: ResearchBrief, draft: Draft) -> Review:
        raise AssertionError("reviewer must not run after a failed research stage")


def test_orchestrator_runs_roles_in_order_and_preserves_all_artifacts() -> None:
    events: list[str] = []
    request = Request("Create a local workflow")
    brief = ResearchBrief("Local workflow", "Explain it", ("No network",), ("Derived",))
    draft = Draft("Local workflow\nExplain it\nNo network")
    review = Review("approved", ("Covered",))
    writer = RecordingWriter(events, draft)
    reviewer = RecordingReviewer(events, review)
    orchestrator = WorkflowOrchestrator(
        researcher=RecordingResearcher(events, brief), writer=writer, reviewer=reviewer
    )

    result = orchestrator.run(request)

    assert events == ["research:Create a local workflow", "writing", "review"]
    assert writer.received_brief is brief
    assert reviewer.received == (brief, draft)
    assert result.request is request
    assert result.research_brief is brief
    assert result.draft is draft
    assert result.review is review
    assert result.phase == ORCHESTRATION_PHASE
    assert result.status == STATUS_COMPLETED


def test_default_orchestrator_is_deterministic() -> None:
    orchestrator = WorkflowOrchestrator()
    request = Request("Explain deterministic contracts")

    assert orchestrator.run(request) == orchestrator.run(request)


def test_orchestrator_wraps_a_stage_failure_and_stops_later_stages() -> None:
    orchestrator = WorkflowOrchestrator(
        researcher=FailingResearcher(),
        writer=UnreachableWriter(),
        reviewer=UnreachableReviewer(),
    )

    with pytest.raises(StageError) as error:
        orchestrator.run(Request("Request"))

    assert error.value.code == "research_stage_failed"
    assert error.value.stage == "research"
    assert isinstance(error.value.__cause__, ValidationError)
