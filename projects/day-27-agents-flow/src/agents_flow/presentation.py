"""JSON presentation for validated workflow results."""

from __future__ import annotations

from .contracts import (
    ORCHESTRATION_PHASE,
    STATUS_COMPLETED,
    WorkflowResult,
)
from .errors import ValidationError


def serialize_workflow(result: WorkflowResult, output_format: str = "json") -> dict[str, object]:
    """Convert a completed workflow result into the stable public JSON document."""

    if output_format != "json":
        raise ValidationError("invalid_format", "format must be 'json'")
    if result.phase != ORCHESTRATION_PHASE or result.status != STATUS_COMPLETED:
        raise ValidationError(
            "invalid_workflow_result",
            "result must be a completed orchestration workflow",
        )
    if result.research_brief is None or result.draft is None or result.review is None:
        raise ValidationError(
            "invalid_workflow_result",
            "completed workflow result must include all role artifacts",
        )

    return {
        "format": output_format,
        "phase": result.phase,
        "status": result.status,
        "request": {"prompt": result.request.prompt},
        "research_brief": {
            "topic": result.research_brief.topic,
            "objective": result.research_brief.objective,
            "constraints": list(result.research_brief.constraints),
            "findings": list(result.research_brief.findings),
        },
        "draft": {"content": result.draft.content},
        "review": {
            "decision": result.review.decision,
            "observations": list(result.review.observations),
        },
        "decision": result.review.decision,
    }
