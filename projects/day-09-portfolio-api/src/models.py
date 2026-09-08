"""Pydantic domain models for validating local portfolio fixtures.

These models validate the Phase 2 fixture source only. They do not expose HTTP
responses, implement routes, apply collection ordering, or provide queries.
"""

from __future__ import annotations

import re
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)


SLUG_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
MONTH_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")

NonEmptyString = Annotated[str, Field(min_length=1, max_length=500)]
ShortText = Annotated[str, Field(min_length=1, max_length=160)]
Summary = Annotated[str, Field(min_length=1, max_length=500)]
Description = Annotated[str, Field(min_length=1, max_length=2_000)]
Month = Annotated[str, Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")]
Slug = Annotated[str, Field(min_length=1, max_length=80, pattern=SLUG_PATTERN)]


class FixtureModel(BaseModel):
    """Reject undeclared fields and normalize textual values used by fixtures."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class PublicLink(FixtureModel):
    """A safe public HTTP(S) link embedded in profile or project data."""

    label: ShortText
    url: HttpUrl


class PublicProfile(FixtureModel):
    """The single public profile payload allowed in the fixture catalog."""

    name: Annotated[str, Field(min_length=1, max_length=120)]
    headline: ShortText
    summary: Summary
    location: ShortText | None = None
    links: list[PublicLink] | None = Field(default=None, max_length=5)


class Project(FixtureModel):
    """A portfolio project payload, including source-only visibility metadata."""

    public: bool
    slug: Slug
    title: ShortText
    summary: Summary
    description: Description
    technologies: list[NonEmptyString] = Field(min_length=1, max_length=20)
    status: Literal["active", "completed", "archived"]
    featured: bool
    published_at: Month | None = None
    links: list[PublicLink] | None = Field(default=None, max_length=3)

    @field_validator("technologies")
    @classmethod
    def technologies_are_unique(cls, values: list[str]) -> list[str]:
        """Keep source technology values unique while preserving their declared order."""
        if len({value.casefold() for value in values}) != len(values):
            raise ValueError("technologies must be unique ignoring case")
        return values


class Skill(FixtureModel):
    """A public skill payload, including source-only visibility metadata."""

    public: bool
    name: ShortText
    category: Literal["backend", "frontend", "data", "cloud", "tools", "other"]
    context: Summary | None = None


class Experience(FixtureModel):
    """A public experience payload, including source-only visibility metadata."""

    public: bool
    organization: ShortText
    role: ShortText
    summary: Summary
    started_at: Month
    ended_at: Month | None = None
    technologies: list[NonEmptyString] | None = Field(default=None, max_length=20)

    @field_validator("technologies")
    @classmethod
    def technologies_are_unique(cls, values: list[str] | None) -> list[str] | None:
        """Keep optional source technology values unique without reordering them."""
        if values is not None and len({value.casefold() for value in values}) != len(values):
            raise ValueError("technologies must be unique ignoring case")
        return values

    @model_validator(mode="after")
    def ending_month_is_not_before_starting_month(self) -> "Experience":
        """Enforce the inclusive chronological relationship in the HTTP contract."""
        if self.ended_at is not None and self.ended_at < self.started_at:
            raise ValueError("ended_at must be equal to or later than started_at")
        return self


class FixtureCatalog(FixtureModel):
    """Validated local source catalog; it is not an HTTP response model."""

    version: Literal[1]
    profile: PublicProfile
    profile_public: Literal[True]
    projects: list[Project]
    skills: list[Skill]
    experience: list[Experience]

    @model_validator(mode="after")
    def public_entities_are_unique(self) -> "FixtureCatalog":
        """Validate the cross-record identity rules that Pydantic fields cannot express."""
        public_slugs = [project.slug for project in self.projects if project.public]
        if len(set(public_slugs)) != len(public_slugs):
            raise ValueError("public project slugs must be unique")

        public_skill_keys = [
            (skill.category, skill.name.casefold())
            for skill in self.skills
            if skill.public
        ]
        if len(set(public_skill_keys)) != len(public_skill_keys):
            raise ValueError("public skill category/name pairs must be unique")
        return self
