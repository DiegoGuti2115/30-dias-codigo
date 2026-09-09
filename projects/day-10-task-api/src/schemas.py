"""Pydantic data contracts for the task API.

This module implements only the Phase 3 validation boundary. It does not
contain persistence, business operations, HTTP routes, or application setup.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StrictBool, field_validator, model_validator


Title = Annotated[str, Field(min_length=1, max_length=120, strict=True)]
Description = Annotated[str, Field(max_length=1_000, strict=True)]


class TaskInputBase(BaseModel):
    """Common editable fields and validation rules for a task."""

    model_config = ConfigDict(extra="forbid", strict=True)

    @field_validator("title", mode="before", check_fields=False)
    @classmethod
    def normalize_title(cls, value: object) -> object:
        """Trim titles before their documented length constraints are checked."""
        if not isinstance(value, str):
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("title must not be empty or contain only whitespace")
        return normalized


class TaskCreate(TaskInputBase):
    """Client payload accepted when creating a task."""

    title: Title
    description: Description | None = None
    completed: StrictBool = False

class TaskReplace(TaskInputBase):
    """Complete editable representation required for a PUT replacement."""

    title: Title
    description: Description | None
    completed: StrictBool

class TaskUpdate(TaskInputBase):
    """Partial editable representation accepted by a PATCH update."""

    title: Title | None = None
    description: Description | None = None
    completed: StrictBool | None = None

    @model_validator(mode="after")
    def validate_partial_update(self) -> "TaskUpdate":
        """Require an editable field and normalize a supplied title."""
        if not self.model_fields_set:
            raise ValueError("at least one editable field is required")
        if "title" in self.model_fields_set and self.title is None:
            raise ValueError("title must be a string when supplied")
        return self


class TaskRead(BaseModel):
    """Complete task representation returned to API consumers."""

    model_config = ConfigDict(extra="forbid", strict=True)

    id: Annotated[int, Field(gt=0, strict=True)]
    title: Title
    description: Description | None
    completed: StrictBool
    created_at: datetime
    updated_at: datetime

    @field_validator("title", mode="before")
    @classmethod
    def normalize_title(cls, value: object) -> object:
        """Normalize an output title using the same invariant as input models."""
        return TaskInputBase.normalize_title(value)

    @model_validator(mode="after")
    def validate_timestamps(self) -> "TaskRead":
        """Ensure output timestamps include timezone information."""
        if self.created_at.tzinfo is None or self.updated_at.tzinfo is None:
            raise ValueError("timestamps must include timezone information")
        return self


class TaskList(BaseModel):
    """Collection response shape defined by the public API contract."""

    model_config = ConfigDict(extra="forbid", strict=True)

    items: list[TaskRead]
