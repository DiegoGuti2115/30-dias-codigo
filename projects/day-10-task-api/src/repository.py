"""Deterministic in-memory persistence for tasks."""

from __future__ import annotations

from collections.abc import Iterable

from src.schemas import TaskRead


class InMemoryTaskRepository:
    """Store tasks by identifier in insertion order for one application instance."""

    def __init__(self) -> None:
        self._tasks: dict[int, TaskRead] = {}
        self._next_id = 1

    def allocate_id(self) -> int:
        """Return a unique, monotonically increasing identifier."""
        task_id = self._next_id
        self._next_id += 1
        return task_id

    def add(self, task: TaskRead) -> TaskRead:
        """Persist a new task and return an isolated copy of it."""
        if task.id in self._tasks:
            raise ValueError(f"task with id {task.id} already exists")
        self._tasks[task.id] = task.model_copy(deep=True)
        return self._copy(task)

    def get(self, task_id: int) -> TaskRead | None:
        """Return one task, or ``None`` when it is absent."""
        task = self._tasks.get(task_id)
        return self._copy(task) if task is not None else None

    def list(self) -> Iterable[TaskRead]:
        """Return tasks in deterministic creation order."""
        return tuple(self._copy(task) for task in self._tasks.values())

    def replace(self, task: TaskRead) -> TaskRead | None:
        """Replace an existing task, returning ``None`` when it is absent."""
        if task.id not in self._tasks:
            return None
        self._tasks[task.id] = task.model_copy(deep=True)
        return self._copy(task)

    def delete(self, task_id: int) -> bool:
        """Delete a task and report whether it existed."""
        if task_id not in self._tasks:
            return False
        del self._tasks[task_id]
        return True

    @staticmethod
    def _copy(task: TaskRead) -> TaskRead:
        """Prevent callers from mutating stored model instances."""
        return task.model_copy(deep=True)
