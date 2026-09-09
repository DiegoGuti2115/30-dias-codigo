"""Domain errors for the task service layer."""


class TaskNotFoundError(LookupError):
    """Raised when an operation targets a task that does not exist."""

    def __init__(self, task_id: int) -> None:
        self.task_id = task_id
        super().__init__(f"task with id {task_id} was not found")
