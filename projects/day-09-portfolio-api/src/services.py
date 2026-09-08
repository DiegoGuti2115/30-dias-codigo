"""Deterministic read-only portfolio queries over validated local entities.

This module applies public visibility and the v1 collection ordering rules. It returns
domain models only; HTTP response projection and transport handling are Phase 4 work.
"""

from __future__ import annotations

from errors import ProjectNotFoundError
from models import Experience, Project, PublicProfile, Skill
from repository import FixtureRepository


class PortfolioQueryService:
    """Compose the public portfolio view from a local fixture repository."""

    def __init__(self, repository: FixtureRepository) -> None:
        self._repository = repository

    def get_profile(self) -> PublicProfile:
        """Return the required public profile from the validated catalog."""
        catalog = self._repository.get_catalog()
        if not catalog.profile_public:
            raise RuntimeError("validated catalog must have a public profile")
        return catalog.profile

    def list_projects(self) -> tuple[Project, ...]:
        """Return public projects in the exact v1 deterministic order."""
        public_projects = (project for project in self._repository.get_projects() if project.public)
        return tuple(sorted(public_projects, key=_project_sort_key))

    def get_project_by_slug(self, slug: str) -> Project:
        """Return one public project by exact slug or raise a controlled absence error."""
        for project in self._repository.get_projects():
            if project.public and project.slug == slug:
                return project
        raise ProjectNotFoundError(slug)

    def list_skills(self) -> tuple[Skill, ...]:
        """Return public skills in category and name order required by v1."""
        public_skills = (skill for skill in self._repository.get_skills() if skill.public)
        return tuple(sorted(public_skills, key=lambda skill: (skill.category, skill.name, skill.name)))

    def list_experience(self) -> tuple[Experience, ...]:
        """Return public experience in the exact v1 deterministic chronological order."""
        public_experience = (entry for entry in self._repository.get_experience() if entry.public)
        return tuple(sorted(public_experience, key=_experience_sort_key))


def _project_sort_key(project: Project) -> tuple[bool, bool, int, int, str]:
    """Sort featured projects first, then dated projects, then stable slug order."""
    year, month = _month_sort_parts(project.published_at)
    return (not project.featured, project.published_at is None, -year, -month, project.slug)


def _experience_sort_key(entry: Experience) -> tuple[int, int, bool, int, int, str, str]:
    """Sort start/end months descending while placing ongoing entries first on ties."""
    start_year, start_month = _month_sort_parts(entry.started_at)
    end_year, end_month = _month_sort_parts(entry.ended_at)
    return (
        -start_year,
        -start_month,
        entry.ended_at is not None,
        -end_year,
        -end_month,
        entry.organization,
        entry.role,
    )


def _month_sort_parts(value: str | None) -> tuple[int, int]:
    """Split a contract-valid monthly value for descending chronological sorting."""
    if value is None:
        return (0, 0)
    year, month = value.split("-", maxsplit=1)
    return (int(year), int(month))
