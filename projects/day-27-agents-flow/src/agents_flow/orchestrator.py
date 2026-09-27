"""Deterministic use case that coordinates local role contracts in a fixed order."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from .agents import LocalResearcher, LocalReviewer, LocalWriter
from .contracts import (
    ORCHESTRATION_PHASE,
    STATUS_COMPLETED,
    Draft,
    Request,
    ResearchBrief,
    Review,
    WorkflowResult,
)
from .errors import DomainError, StageError


class Researcher(Protocol):
    """Port for a role that turns a request into a research brief."""

    def research(self, request: Request) -> ResearchBrief:
        """Produce a validated research brief."""


class Writer(Protocol):
    """Port for a role that turns a research brief into a draft."""

    def write(self, brief: ResearchBrief) -> Draft:
        """Produce a validated draft."""


class Reviewer(Protocol):
    """Port for a role that evaluates a brief and its draft."""

    def review(self, brief: ResearchBrief, draft: Draft) -> Review:
        """Produce a validated review."""


@dataclass(slots=True)
class WorkflowOrchestrator:
    """Execute research, writing, and review without shared mutable workflow state."""

    researcher: Researcher = field(default_factory=LocalResearcher)
    writer: Writer = field(default_factory=LocalWriter)
    reviewer: Reviewer = field(default_factory=LocalReviewer)

    def run(self, request: Request) -> WorkflowResult:
        """Execute all roles in order and retain every successful intermediate artifact."""

        brief = self._run_stage("research", self.researcher.research, request)
        draft = self._run_stage("writing", self.writer.write, brief)
        review = self._run_stage("review", self.reviewer.review, brief, draft)
        return WorkflowResult(
            request=request,
            research_brief=brief,
            draft=draft,
            review=review,
            phase=ORCHESTRATION_PHASE,
            status=STATUS_COMPLETED,
        )

    @staticmethod
    def _run_stage(stage: str, operation, *arguments):
        """Translate unexpected role failures into stable stage-specific domain errors."""

        try:
            return operation(*arguments)
        except StageError:
            raise
        except DomainError as error:
            raise StageError(stage, error) from error
        except Exception as error:
            raise StageError(stage, error) from error
