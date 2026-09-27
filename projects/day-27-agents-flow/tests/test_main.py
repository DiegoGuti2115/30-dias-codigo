"""End-to-end tests for the Phase 4 JSON command-line interface."""

from __future__ import annotations

import io
import json

import pytest

from agents_flow.contracts import Request, WorkflowResult
from agents_flow.errors import StageError, ValidationError
from agents_flow.main import VALIDATION_EXIT_CODE, build_parser, main, serialize_contract


class FailingOrchestrator:
    def run(self, request: Request) -> WorkflowResult:
        raise StageError("research", ValidationError("invalid_research", "cannot research"))


def test_main_prints_the_completed_traceable_workflow_document() -> None:
    stdout = io.StringIO()
    stderr = io.StringIO()

    exit_code = main(["Explica el contrato"], stdout=stdout, stderr=stderr)

    document = json.loads(stdout.getvalue())
    assert exit_code == 0
    assert stderr.getvalue() == ""
    assert document["format"] == "json"
    assert document["phase"] == 3
    assert document["status"] == "completed"
    assert document["request"] == {"prompt": "Explica el contrato"}
    assert document["research_brief"]["topic"] == "Explica el contrato"
    assert document["draft"]["content"].startswith("Explica el contrato")
    assert document["review"]["decision"] == "approved"
    assert document["decision"] == "approved"


@pytest.mark.parametrize(
    ("argv", "code"),
    [
        ([], "invalid_prompt_type"),
        ([""], "invalid_prompt"),
        (["   "], "invalid_prompt"),
    ],
)
def test_main_sends_stable_validation_errors_to_stderr_only(
    argv: list[str], code: str
) -> None:
    stdout = io.StringIO()
    stderr = io.StringIO()

    exit_code = main(argv, stdout=stdout, stderr=stderr)

    assert exit_code == VALIDATION_EXIT_CODE
    assert stdout.getvalue() == ""
    assert json.loads(stderr.getvalue())["error"]["code"] == code


def test_main_serializes_stage_errors_to_stderr_only() -> None:
    stdout = io.StringIO()
    stderr = io.StringIO()

    exit_code = main(
        ["Solicitud"],
        stdout=stdout,
        stderr=stderr,
        orchestrator=FailingOrchestrator(),  # type: ignore[arg-type]
    )

    assert exit_code == VALIDATION_EXIT_CODE
    assert stdout.getvalue() == ""
    assert json.loads(stderr.getvalue()) == {
        "error": {
            "code": "research_stage_failed",
            "message": "research stage failed: cannot research",
        }
    }


def test_help_describes_the_same_arguments_as_the_cli_contract(capsys) -> None:
    with pytest.raises(SystemExit) as error:
        build_parser().parse_args(["--help"])

    assert error.value.code == 0
    help_text = capsys.readouterr().out
    assert "prompt" in help_text
    assert "--format" in help_text
    assert "investigación, redacción y revisión" in help_text


def test_parser_rejects_an_unsupported_output_format() -> None:
    with pytest.raises(SystemExit) as error:
        main(["Solicitud", "--format", "text"])

    assert error.value.code == 2


def test_legacy_serializer_remains_available_for_phase_one_contracts() -> None:
    result = WorkflowResult(request=Request("Solicitud"))

    assert serialize_contract(result, "json") == {
        "format": "json",
        "phase": 1,
        "request": {"prompt": "Solicitud"},
        "status": "contract_only",
    }


def test_legacy_serializer_rejects_formats_outside_the_contract() -> None:
    with pytest.raises(ValidationError) as error:
        serialize_contract(WorkflowResult(request=Request("Solicitud")), "text")

    assert error.value.code == "invalid_format"
