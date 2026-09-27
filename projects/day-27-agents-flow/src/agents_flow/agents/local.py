"""Deterministic local role adapters with no network, files, or shared state."""

from __future__ import annotations

from ..contracts import Draft, Request, ResearchBrief, Review


class LocalResearcher:
    """Derive a structured brief directly from the request text."""

    def research(self, request: Request) -> ResearchBrief:
        """Return the same validated brief for an equivalent request every time."""

        prompt = request.prompt.strip()
        topic = prompt.rstrip(".?!")
        return ResearchBrief(
            topic=topic,
            objective=f"Address the request: {prompt}",
            constraints=(
                "Use only information derived from the request.",
                "Do not claim external research or sources.",
            ),
            findings=(
                f"The requested topic is: {topic}.",
                "The output must be concise, clear, and directly responsive.",
            ),
        )


class LocalWriter:
    """Create a predictable editorial draft from a research brief."""

    def write(self, brief: ResearchBrief) -> Draft:
        """Build a draft using only the role input contract."""

        findings = " ".join(brief.findings)
        constraints = " ".join(brief.constraints)
        return Draft(
            content=(
                f"{brief.topic}\n\n"
                f"Objective: {brief.objective}\n\n"
                f"Key points: {findings}\n\n"
                f"Constraints: {constraints}"
            )
        )


class LocalReviewer:
    """Evaluate coverage, clarity, and constraints using explicit local rules."""

    def review(self, brief: ResearchBrief, draft: Draft) -> Review:
        """Return an approval or actionable observations without rewriting the draft."""

        content = draft.content.casefold()
        expected_fragments = (brief.topic, brief.objective, *brief.constraints)
        missing = tuple(
            f"Missing required coverage: {fragment}"
            for fragment in expected_fragments
            if fragment.casefold() not in content
        )
        if missing:
            return Review(decision="changes_requested", observations=missing)
        return Review(
            decision="approved",
            observations=(
                "The draft covers the topic, objective, and declared constraints.",
                "The draft is structurally clear for the local workflow.",
            ),
        )
