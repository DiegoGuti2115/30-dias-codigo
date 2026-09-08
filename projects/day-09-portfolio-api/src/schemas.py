"""Public HTTP response schemas and explicit projections for portfolio v1.

These models intentionally differ from Phase 2 fixture models: they exclude source-only
visibility metadata and expose only fields defined by the HTTP contract.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from models import Experience, Project, PublicLink, PublicProfile, Skill


class PublicResponseModel(BaseModel):
    """Base model that prevents undeclared fields in public response shapes."""

    model_config = ConfigDict(extra="forbid")


class HealthResponse(PublicResponseModel):
    """Minimal operational response for the application health route."""

    status: Literal["ok"]


class LinkResponse(PublicResponseModel):
    """Public HTTP(S) link representation shared by profile and projects."""

    label: str
    url: str


class ProfileResponse(PublicResponseModel):
    """Public profile representation without source metadata."""

    name: str
    headline: str
    summary: str
    location: str | None = None
    links: list[LinkResponse] | None = Field(default=None, max_length=5)


class ProjectSummaryResponse(PublicResponseModel):
    """Public project list representation, deliberately excluding description."""

    slug: str
    title: str
    summary: str
    technologies: list[str]
    status: Literal["active", "completed", "archived"]
    featured: bool
    published_at: str | None = None
    links: list[LinkResponse] | None = Field(default=None, max_length=3)


class ProjectDetailResponse(ProjectSummaryResponse):
    """Public project detail representation extending the list view."""

    description: str


class SkillResponse(PublicResponseModel):
    """Public skill representation without source visibility metadata."""

    name: str
    category: Literal["backend", "frontend", "data", "cloud", "tools", "other"]
    context: str | None = None


class ExperienceResponse(PublicResponseModel):
    """Public experience representation without source visibility metadata."""

    organization: str
    role: str
    summary: str
    started_at: str
    ended_at: str | None = None
    technologies: list[str] | None = None


class ProjectListResponse(PublicResponseModel):
    """Response envelope for the ordered public project collection."""

    items: list[ProjectSummaryResponse]


class SkillListResponse(PublicResponseModel):
    """Response envelope for the ordered public skill collection."""

    items: list[SkillResponse]


class ExperienceListResponse(PublicResponseModel):
    """Response envelope for the ordered public experience collection."""

    items: list[ExperienceResponse]


class ErrorBody(PublicResponseModel):
    """Stable public error payload nested inside an error response."""

    code: str
    message: str


class ErrorResponse(PublicResponseModel):
    """Public error response used for controlled domain and source failures."""

    error: ErrorBody


def project_summary_from_domain(project: Project) -> ProjectSummaryResponse:
    """Project one public list representation from a validated domain entity."""
    return ProjectSummaryResponse(
        slug=project.slug,
        title=project.title,
        summary=project.summary,
        technologies=list(project.technologies),
        status=project.status,
        featured=project.featured,
        published_at=project.published_at,
        links=_links_from_domain(project.links),
    )


def project_detail_from_domain(project: Project) -> ProjectDetailResponse:
    """Project one public detail representation from a validated domain entity."""
    return ProjectDetailResponse(
        **project_summary_from_domain(project).model_dump(),
        description=project.description,
    )


def profile_from_domain(profile: PublicProfile) -> ProfileResponse:
    """Project the single source profile into its contract-defined public shape."""
    return ProfileResponse(
        name=profile.name,
        headline=profile.headline,
        summary=profile.summary,
        location=profile.location,
        links=_links_from_domain(profile.links),
    )


def skill_from_domain(skill: Skill) -> SkillResponse:
    """Project a domain skill without its internal visibility marker."""
    return SkillResponse(name=skill.name, category=skill.category, context=skill.context)


def experience_from_domain(entry: Experience) -> ExperienceResponse:
    """Project a domain experience without its internal visibility marker."""
    return ExperienceResponse(
        organization=entry.organization,
        role=entry.role,
        summary=entry.summary,
        started_at=entry.started_at,
        ended_at=entry.ended_at,
        technologies=list(entry.technologies) if entry.technologies is not None else None,
    )


def _links_from_domain(links: list[PublicLink] | None) -> list[LinkResponse] | None:
    """Serialize validated URL objects as plain public JSON strings."""
    if links is None:
        return None
    return [LinkResponse(label=link.label, url=str(link.url)) for link in links]
