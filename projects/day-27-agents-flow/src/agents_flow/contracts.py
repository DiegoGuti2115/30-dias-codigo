"""Immutable contracts and semantic validation for the local agent workflow."""

from __future__ import annotations

from dataclasses import dataclass

from .errors import ValidationError

PHASE = 1
ORCHESTRATION_PHASE = 3
STATUS_CONTRACT_ONLY = "contract_only"
STATUS_COMPLETED = "completed"
REVIEW_DECISIONS = ("approved", "changes_requested")


def _require_text(value: object, field: str) -> None:
    """Validate a non-blank textual contract field with a stable error code."""

    if not isinstance(value, str):
        raise ValidationError(f"invalid_{field}_type", f"{field} must be a text string")
    if not value.strip():
        raise ValidationError(
            f"invalid_{field}", f"{field} must contain non-whitespace text"
        )


def _require_text_tuple(value: object, field: str) -> None:
    """Validate an immutable non-empty collection of non-blank text values."""

    if not isinstance(value, tuple):
        raise ValidationError(f"invalid_{field}_type", f"{field} must be a tuple of text")
    if not value:
        raise ValidationError(f"invalid_{field}", f"{field} must not be empty")
    for item in value:
        _require_text(item, field[:-1])


@dataclass(frozen=True, slots=True)
class Request:
    """Validated textual request received by the workflow."""

    prompt: str

    def __post_init__(self) -> None:
        _require_text(self.prompt, "prompt")


@dataclass(frozen=True, slots=True)
class ResearchBrief:
    """Structured, locally-derived research artifact for the writer role."""

    topic: str
    objective: str
    constraints: tuple[str, ...]
    findings: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_text(self.topic, "topic")
        _require_text(self.objective, "objective")
        _require_text_tuple(self.constraints, "constraints")
        _require_text_tuple(self.findings, "findings")


@dataclass(frozen=True, slots=True)
class Draft:
    """Writer artifact built exclusively from a valid research brief."""

    content: str

    def __post_init__(self) -> None:
        _require_text(self.content, "content")


@dataclass(frozen=True, slots=True)
class Review:
    """Traceable reviewer decision and its deterministic observations."""

    decision: str
    observations: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.decision not in REVIEW_DECISIONS:
            raise ValidationError(
                "invalid_decision",
                "decision must be 'approved' or 'changes_requested'",
            )
        if not isinstance(self.observations, tuple):
            raise ValidationError(
                "invalid_observations_type", "observations must be a tuple of text"
            )
        for observation in self.observations:
            _require_text(observation, "observation")
        if self.decision == "changes_requested" and not self.observations:
            raise ValidationError(
                "invalid_observations",
                "changes_requested review must include at least one observation",
            )


@dataclass(frozen=True, slots=True)
class WorkflowResult:
    """Traceable workflow state for the legacy contract or a completed orchestration."""

    request: Request
    research_brief: ResearchBrief | None = None
    draft: Draft | None = None
    review: Review | None = None
    phase: int = PHASE
    status: str = STATUS_CONTRACT_ONLY

    def __post_init__(self) -> None:
        artifacts = (self.research_brief, self.draft, self.review)
        if not isinstance(self.request, Request):
            raise ValidationError("invalid_request_type", "request must be a Request")
        if self.phase == PHASE and self.status == STATUS_CONTRACT_ONLY:
            if any(artifact is not None for artifact in artifacts):
                raise ValidationError(
                    "invalid_workflow_artifacts",
                    "contract_only result must not include role artifacts",
                )
            return
        if self.phase == ORCHESTRATION_PHASE and self.status == STATUS_COMPLETED:
            if not isinstance(self.research_brief, ResearchBrief):
                raise ValidationError(
                    "invalid_research_brief", "completed result must include a ResearchBrief"
                )
            if not isinstance(self.draft, Draft):
                raise ValidationError("invalid_draft", "completed result must include a Draft")
            if not isinstance(self.review, Review):
                raise ValidationError("invalid_review", "completed result must include a Review")
            return
        if self.phase not in (PHASE, ORCHESTRATION_PHASE):
            raise ValidationError(
                "invalid_phase",
                f"phase must be {PHASE} or {ORCHESTRATION_PHASE}",
            )
        raise ValidationError(
            "invalid_status",
            "status must match the selected workflow phase",
        )
