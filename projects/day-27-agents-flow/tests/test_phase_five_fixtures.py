"""Fixture-backed integration coverage for the deterministic local workflow."""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from agents_flow.agents import LocalReviewer
from agents_flow.contracts import Draft, Request, ResearchBrief
from agents_flow.errors import StageError, ValidationError
from agents_flow.main import VALIDATION_EXIT_CODE, main
from agents_flow.orchestrator import WorkflowOrchestrator
from agents_flow.presentation import serialize_workflow

FIXTURE_PATH = Path(__file__).parents[1] / "data" / "workflow_cases.json"


@pytest.fixture(scope="module")
def workflow_cases() -> dict[str, object]:
    """Load stable, local scenarios without external services or credentials."""

    with FIXTURE_PATH.open(encoding="utf-8") as fixture_file:
        return json.load(fixture_file)


def test_approved_fixture_drives_an_end_to_end_traceable_result(
    workflow_cases: dict[str, object],
) -> None:
    approved = workflow_cases["approved"]
    assert isinstance(approved, dict)
    expected = approved["expected"]
    assert isinstance(expected, dict)

    result = WorkflowOrchestrator().run(Request(approved["prompt"]))
    document = serialize_workflow(result)

    assert document["research_brief"]["topic"] == expected["topic"]
    assert document["review"]["decision"] == expected["decision"]
    assert document["review"]["observations"] == expected["observations"]
    assert document["decision"] == expected["decision"]
    assert result == WorkflowOrchestrator().run(Request(approved["prompt"]))


def test_changes_requested_fixture_covers_each_missing_requirement(
    workflow_cases: dict[str, object],
) -> None:
    scenario = workflow_cases["changes_requested"]
    assert isinstance(scenario, dict)
    brief_data = scenario["brief"]
    expected = scenario["expected"]
    assert isinstance(brief_data, dict)
    assert isinstance(expected, dict)

    brief = ResearchBrief(
        topic=brief_data["topic"],
        objective=brief_data["objective"],
        constraints=tuple(brief_data["constraints"]),
        findings=tuple(brief_data["findings"]),
    )
    review = LocalReviewer().review(brief, Draft(scenario["draft"]))

    assert review.decision == expected["decision"]
    assert list(review.observations) == expected["observations"]


def test_invalid_request_fixture_stops_before_any_agent_stage(
    workflow_cases: dict[str, object],
) -> None:
    invalid_request = workflow_cases["invalid_request"]
    assert isinstance(invalid_request, dict)

    with pytest.raises(ValidationError) as error:
        Request(invalid_request["prompt"])

    assert error.value.code == invalid_request["expected_error_code"]


@pytest.mark.parametrize("stage", ["writing", "review"])
def test_orchestrator_wraps_later_stage_failures_from_fixture_coverage(stage: str) -> None:
    class FailingWriter:
        def write(self, brief: ResearchBrief) -> Draft:
            raise ValidationError("invalid_draft", "fixture writer failure")

    class FailingReviewer:
        def review(self, brief: ResearchBrief, draft: Draft):
            raise RuntimeError("fixture reviewer failure")

    orchestrator = WorkflowOrchestrator(
        writer=FailingWriter() if stage == "writing" else WorkflowOrchestrator().writer,
        reviewer=FailingReviewer() if stage == "review" else WorkflowOrchestrator().reviewer,
    )

    with pytest.raises(StageError) as error:
        orchestrator.run(Request("Exercise stage errors"))

    assert error.value.code == f"{stage}_stage_failed"
    assert error.value.stage == stage


def test_cli_uses_the_fixture_prompt_and_preserves_utf8_json(
    workflow_cases: dict[str, object],
) -> None:
    approved = workflow_cases["approved"]
    assert isinstance(approved, dict)
    stdout = io.StringIO()
    stderr = io.StringIO()

    exit_code = main([approved["prompt"]], stdout=stdout, stderr=stderr)

    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert "trazabilidad" in stdout.getvalue()
    assert json.loads(stdout.getvalue())["decision"] == "approved"


def test_cli_reports_the_fixture_validation_error_as_json_only_on_stderr(
    workflow_cases: dict[str, object],
) -> None:
    invalid_request = workflow_cases["invalid_request"]
    assert isinstance(invalid_request, dict)
    stdout = io.StringIO()
    stderr = io.StringIO()

    exit_code = main([invalid_request["prompt"]], stdout=stdout, stderr=stderr)

    assert exit_code == VALIDATION_EXIT_CODE
    assert stdout.getvalue() == ""
    assert json.loads(stderr.getvalue())["error"]["code"] == invalid_request["expected_error_code"]
