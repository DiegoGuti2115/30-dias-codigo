"""Local, read-only access to the validated portfolio fixture catalog.

The repository owns fixture loading and exposes validated domain entities. It does not
filter visibility, order collections, or project HTTP response shapes.
"""

from __future__ import annotations

from pathlib import Path

from errors import FixtureSourceError
from fixtures import FixtureLoadError, load_fixture_catalog
from models import Experience, FixtureCatalog, Project, PublicProfile, Skill


class FixtureRepository:
    """Load one fixture catalog once and provide its immutable validated entities."""

    def __init__(self, fixture_path: Path) -> None:
        self._fixture_path = fixture_path
        self._catalog: FixtureCatalog | None = None

    def get_catalog(self) -> FixtureCatalog:
        """Return the cached validated catalog, loading it on first access only."""
        if self._catalog is None:
            try:
                self._catalog = load_fixture_catalog(self._fixture_path)
            except FixtureLoadError as error:
                raise FixtureSourceError("portfolio fixture source is unavailable") from error
        return self._catalog

    def get_profile(self) -> PublicProfile:
        """Return the single validated profile source entity."""
        return self.get_catalog().profile

    def get_projects(self) -> tuple[Project, ...]:
        """Return projects in physical fixture order without applying visibility rules."""
        return tuple(self.get_catalog().projects)

    def get_skills(self) -> tuple[Skill, ...]:
        """Return skills in physical fixture order without applying visibility rules."""
        return tuple(self.get_catalog().skills)

    def get_experience(self) -> tuple[Experience, ...]:
        """Return experience in physical fixture order without applying visibility rules."""
        return tuple(self.get_catalog().experience)
