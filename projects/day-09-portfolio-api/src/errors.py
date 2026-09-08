"""Controlled domain errors for the local portfolio query layer.

These exceptions carry no HTTP status or transport response format. FastAPI mapping is
intentionally deferred to Phase 4.
"""

from __future__ import annotations


class PortfolioQueryError(RuntimeError):
    """Base class for controlled failures raised by portfolio queries."""


class FixtureSourceError(PortfolioQueryError):
    """Raised when the local catalog cannot be loaded as a valid source."""


class ProjectNotFoundError(PortfolioQueryError):
    """Raised when a valid lookup does not identify a public project."""

    def __init__(self, slug: str) -> None:
        super().__init__("public project was not found")
        self.slug = slug
