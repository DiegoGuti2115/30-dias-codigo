"""HTTP-independent CRUD operations for tasks."""

from __future__ import annotations

from datetime import UTC, datetime

from src.errors import TaskNotFoundError
from src.repository import InMemoryTaskRepository
from src.schemas import TaskCreate, TaskList, TaskRead, TaskReplace, TaskUpdate


class TaskService:
    """Coordinate validation-ready task data with local persistence."""

    def __init__(self, repository: InMemoryTaskRepository | None = None) -> None:
        self._repository = repository or InMemoryTaskRepository()

    def create(self, payload: TaskCreate) -> TaskRead:
        """Create a task with server-managed identity and timestamps."""
        timestamp = self._now()
        task = TaskRead(
            id=self._repository.allocate_id(),
            title=payload.title,
            description=payload.description,
            completed=payload.completed,
            created_at=timestamp,
            updated_at=timestamp,
        )
        return self._repository.add(task)

    def get(self, task_id: int) -> TaskRead:
        """Return an existing task or raise a domain-specific missing-resource error."""
        task = self._repository.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def list(self) -> TaskList:
        """Return all tasks in deterministic creation order."""
        return TaskList(items=list(self._repository.list()))

    def replace(self, task_id: int, payload: TaskReplace) -> TaskRead:
        """Replace every editable field while preserving identity and creation time."""
        existing = self.get(task_id)
        replacement = TaskRead(
            id=existing.id,
            title=payload.title,
            description=payload.description,
            completed=payload.completed,
            created_at=existing.created_at,
            updated_at=self._now(),
        )
        return self._replace_existing(replacement)

    def update(self, task_id: int, payload: TaskUpdate) -> TaskRead:
        """Apply only explicitly supplied editable fields to an existing task."""
        existing = self.get(task_id)
        changes = payload.model_dump(exclude_unset=True)
        updated = TaskRead(
            id=existing.id,
            title=changes.get("title", existing.title),
            description=changes.get("description", existing.description),
            completed=changes.get("completed", existing.completed),
            created_at=existing.created_at,
            updated_at=self._now(),
        )
        return self._replace_existing(updated)

    def delete(self, task_id: int) -> None:
        """Remove a task or raise the missing-resource error."""
        if not self._repository.delete(task_id):
            raise TaskNotFoundError(task_id)

    def _replace_existing(self, task: TaskRead) -> TaskRead:
        """Persist a replacement and guard against an unexpected concurrent removal."""
        saved = self._repository.replace(task)
        if saved is None:
            raise TaskNotFoundError(task.id)
        return saved

    @staticmethod
    def _now() -> datetime:
        """Produce an aware UTC timestamp for server-managed metadata."""
        return datetime.now(UTC)
