"""Schema-level tests for the Phase 3 task validation boundary."""

from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from src.errors import TaskNotFoundError
from src.main import create_app
from src.repository import InMemoryTaskRepository
from src.schemas import TaskCreate, TaskList, TaskRead, TaskReplace, TaskUpdate
from src.service import TaskService


def test_create_accepts_defaults_and_normalizes_title() -> None:
    """Creation accepts required fields and applies documented defaults."""
    task = TaskCreate(title="  Plan the release  ")

    assert task.title == "Plan the release"
    assert task.description is None
    assert task.completed is False


def test_create_accepts_empty_description() -> None:
    """An explicit empty description remains distinct from a null description."""
    task = TaskCreate(title="Document API", description="")

    assert task.description == ""


@pytest.mark.parametrize(
    "title",
    ["", "   ", "x" * 121, 1],
)
def test_create_rejects_invalid_titles(title: object) -> None:
    """Titles must be textual, non-blank, and at most 120 characters."""
    with pytest.raises(ValidationError):
        TaskCreate(title=title)


@pytest.mark.parametrize(
    "description",
    ["x" * 1_001, 42],
)
def test_create_rejects_invalid_descriptions(description: object) -> None:
    """Descriptions may be null or strings of at most 1,000 characters."""
    with pytest.raises(ValidationError):
        TaskCreate(title="Valid title", description=description)


@pytest.mark.parametrize("completed", [1, "true", None])
def test_create_requires_a_strict_boolean_for_completed(completed: object) -> None:
    """The completed field does not coerce non-boolean JSON-like values."""
    with pytest.raises(ValidationError):
        TaskCreate(title="Valid title", completed=completed)


@pytest.mark.parametrize("field", ["id", "created_at", "updated_at", "unexpected"])
def test_input_models_reject_read_only_and_unknown_fields(field: str) -> None:
    """Client input cannot set server-managed fields or arbitrary properties."""
    with pytest.raises(ValidationError):
        TaskCreate.model_validate({"title": "Valid title", field: 1})


def test_replace_requires_every_editable_field() -> None:
    """PUT data must provide title, description, and completed."""
    with pytest.raises(ValidationError):
        TaskReplace.model_validate({"title": "Replace title", "completed": True})

    replacement = TaskReplace(
        title="  Replace title  ",
        description=None,
        completed=True,
    )

    assert replacement.title == "Replace title"
    assert replacement.description is None
    assert replacement.completed is True


def test_partial_update_requires_an_editable_field() -> None:
    """PATCH data cannot be an empty object or contain only unknown fields."""
    with pytest.raises(ValidationError, match="at least one editable field"):
        TaskUpdate()
    with pytest.raises(ValidationError):
        TaskUpdate.model_validate({"id": 1})


def test_partial_update_preserves_explicit_null_description() -> None:
    """PATCH accepts null to remove an optional description."""
    update = TaskUpdate.model_validate({"description": None})

    assert update.description is None
    assert update.model_fields_set == {"description"}


def test_partial_update_rejects_null_title() -> None:
    """A title is optional only by omission, never by a null value."""
    with pytest.raises(ValidationError, match="title must be a string"):
        TaskUpdate.model_validate({"title": None})


def test_read_model_requires_positive_id_and_aware_timestamps() -> None:
    """Server representations enforce identifier and timestamp invariants."""
    timestamp = datetime(2026, 9, 8, 12, 0, tzinfo=UTC)
    task = TaskRead(
        id=1,
        title="  Read model  ",
        description=None,
        completed=False,
        created_at=timestamp,
        updated_at=timestamp,
    )

    assert task.id == 1
    assert task.title == "Read model"

    with pytest.raises(ValidationError):
        TaskRead(
            id=0,
            title="Read model",
            description=None,
            completed=False,
            created_at=timestamp,
            updated_at=timestamp,
        )
    with pytest.raises(ValidationError):
        TaskRead(
            id="1",
            title="Read model",
            description=None,
            completed=False,
            created_at=timestamp,
            updated_at=timestamp,
        )
    with pytest.raises(ValidationError, match="timezone"):
        TaskRead(
            id=1,
            title="Read model",
            description=None,
            completed=False,
            created_at=datetime(2026, 9, 8, 12, 0),
            updated_at=timestamp,
        )


def test_list_model_contains_complete_task_representations() -> None:
    """The list response is an object with an items collection."""
    timestamp = datetime(2026, 9, 8, 12, 0, tzinfo=UTC)
    response = TaskList.model_validate(
        {
            "items": [
                {
                    "id": 1,
                    "title": "First task",
                    "description": None,
                    "completed": False,
                    "created_at": timestamp,
                    "updated_at": timestamp,
                }
            ]
        }
    )

    assert [task.id for task in response.items] == [1]


def test_service_creates_tasks_with_unique_ids_and_aware_timestamps() -> None:
    """A fresh service owns isolated state and generates server-managed metadata."""
    service = TaskService()

    first = service.create(TaskCreate(title="  First  "))
    second = service.create(TaskCreate(title="Second", completed=True))

    assert (first.id, second.id) == (1, 2)
    assert first.title == "First"
    assert first.description is None
    assert second.completed is True
    assert first.created_at.tzinfo is not None
    assert first.created_at == first.updated_at


def test_service_lists_tasks_in_creation_order_and_isolates_instances() -> None:
    """Listing is deterministic and repositories do not share local state."""
    service = TaskService()
    service.create(TaskCreate(title="First"))
    service.create(TaskCreate(title="Second"))

    listed = service.list()
    other_service = TaskService()

    assert [task.title for task in listed.items] == ["First", "Second"]
    assert other_service.list().items == []


def test_service_get_and_delete_raise_for_missing_tasks() -> None:
    """Missing-resource behavior is consistent across reads and deletions."""
    service = TaskService()

    with pytest.raises(TaskNotFoundError, match="id 99"):
        service.get(99)
    with pytest.raises(TaskNotFoundError, match="id 99"):
        service.delete(99)

    task = service.create(TaskCreate(title="Disposable"))
    service.delete(task.id)

    with pytest.raises(TaskNotFoundError, match=f"id {task.id}"):
        service.get(task.id)


def test_service_replace_preserves_server_managed_fields() -> None:
    """A complete replacement retains the resource identity and creation timestamp."""
    service = TaskService()
    original = service.create(TaskCreate(title="Original", description="Old"))

    replacement = service.replace(
        original.id,
        TaskReplace(title="Replacement", description=None, completed=True),
    )

    assert replacement.id == original.id
    assert replacement.created_at == original.created_at
    assert replacement.updated_at >= original.updated_at
    assert (replacement.title, replacement.description, replacement.completed) == (
        "Replacement",
        None,
        True,
    )


def test_service_partial_update_changes_only_supplied_fields() -> None:
    """Partial updates support explicit null descriptions and preserve other values."""
    service = TaskService()
    original = service.create(
        TaskCreate(title="Original", description="Keep until cleared", completed=False)
    )

    updated = service.update(
        original.id,
        TaskUpdate.model_validate({"description": None, "completed": True}),
    )

    assert updated.id == original.id
    assert updated.created_at == original.created_at
    assert updated.updated_at >= original.updated_at
    assert updated.title == "Original"
    assert updated.description is None
    assert updated.completed is True


def test_service_updates_and_replacements_raise_for_missing_tasks() -> None:
    """Write operations report absent resources through the domain error."""
    service = TaskService()

    with pytest.raises(TaskNotFoundError):
        service.replace(
            1,
            TaskReplace(title="Missing", description=None, completed=False),
        )
    with pytest.raises(TaskNotFoundError):
        service.update(1, TaskUpdate(title="Missing"))


def test_repository_returns_copies_and_rejects_duplicate_ids() -> None:
    """Repository callers cannot mutate persisted models and IDs remain unique."""
    repository = InMemoryTaskRepository()
    timestamp = datetime(2026, 9, 8, 12, 0, tzinfo=UTC)
    task = TaskRead(
        id=repository.allocate_id(),
        title="Stored",
        description=None,
        completed=False,
        created_at=timestamp,
        updated_at=timestamp,
    )

    stored = repository.add(task)
    assert stored == task
    with pytest.raises(ValueError, match="already exists"):
        repository.add(task)
    assert repository.get(task.id) == task


def make_client() -> TestClient:
    """Create an application client with isolated in-memory state."""
    return TestClient(create_app())


def test_http_availability_and_openapi_metadata_are_exposed() -> None:
    """The FastAPI application exposes generated documentation and an empty collection."""
    with make_client() as client:
        response = client.get("/api/v1/tasks")
        openapi = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json() == {"items": []}
    assert openapi.status_code == 200
    assert openapi.json()["info"]["title"] == "API CRUD de tareas"
    assert "/api/v1/tasks" in openapi.json()["paths"]


def test_http_crud_flow_matches_the_public_contract() -> None:
    """Every CRUD endpoint delegates to the domain service with documented status codes."""
    with make_client() as client:
        created = client.post("/api/v1/tasks", json={"title": "  Publish API  "})
        task = created.json()
        listed = client.get("/api/v1/tasks")
        fetched = client.get(f"/api/v1/tasks/{task['id']}")
        replaced = client.put(
            f"/api/v1/tasks/{task['id']}",
            json={"title": "Published", "description": "Ready", "completed": True},
        )
        patched = client.patch(
            f"/api/v1/tasks/{task['id']}", json={"description": None}
        )
        deleted = client.delete(f"/api/v1/tasks/{task['id']}")

    assert created.status_code == 201
    assert task["title"] == "Publish API"
    assert task["description"] is None
    assert task["completed"] is False
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()["items"]] == [task["id"]]
    assert fetched.status_code == 200
    assert replaced.status_code == 200
    assert replaced.json()["completed"] is True
    assert patched.status_code == 200
    assert patched.json()["description"] is None
    assert deleted.status_code == 204
    assert deleted.content == b""


def test_http_translates_not_found_and_empty_patch_errors() -> None:
    """Domain and semantic update failures use their stable application error shapes."""
    with make_client() as client:
        missing = client.get("/api/v1/tasks/99")
        empty_patch = client.patch("/api/v1/tasks/1", json={})

    assert missing.status_code == 404
    assert missing.json() == {
        "error": {"code": "task_not_found", "message": "Task 99 was not found."}
    }
    assert empty_patch.status_code == 400
    assert empty_patch.json() == {
        "error": {
            "code": "invalid_request",
            "message": "At least one editable field is required.",
        }
    }


def test_http_preserves_fastapi_validation_for_invalid_input() -> None:
    """Route and payload validation errors retain the framework-standard detail response."""
    with make_client() as client:
        invalid_payload = client.post("/api/v1/tasks", json={"title": "   "})
        invalid_identifier = client.get("/api/v1/tasks/0")
        rejected_read_only = client.post("/api/v1/tasks", json={"title": "Task", "id": 1})

    assert invalid_payload.status_code == 422
    assert isinstance(invalid_payload.json()["detail"], list)
    assert invalid_identifier.status_code == 422
    assert isinstance(invalid_identifier.json()["detail"], list)
    assert rejected_read_only.status_code == 422
    assert isinstance(rejected_read_only.json()["detail"], list)


def test_http_translates_unsupported_methods_to_the_contract_error() -> None:
    """Published paths return the documented error shape for unsupported methods."""
    with make_client() as client:
        response = client.post("/api/v1/tasks/1")

    assert response.status_code == 405
    assert response.json() == {
        "error": {
            "code": "method_not_allowed",
            "message": "The requested method is not allowed for this resource.",
        }
    }


def test_http_list_preserves_creation_order_and_clients_are_isolated() -> None:
    """Every application instance owns isolated state and lists IDs in creation order."""
    with make_client() as first_client:
        first = first_client.post("/api/v1/tasks", json={"title": "First"})
        second = first_client.post("/api/v1/tasks", json={"title": "Second"})
        listed = first_client.get("/api/v1/tasks")

    with make_client() as second_client:
        isolated_list = second_client.get("/api/v1/tasks")

    assert first.status_code == 201
    assert second.status_code == 201
    assert [item["id"] for item in listed.json()["items"]] == [1, 2]
    assert isolated_list.json() == {"items": []}


def test_http_update_preserves_unsupplied_fields_and_accepts_empty_description() -> None:
    """PATCH changes only supplied fields and preserves a deliberate empty string."""
    with make_client() as client:
        created = client.post(
            "/api/v1/tasks",
            json={"title": "Original", "description": "Existing", "completed": False},
        ).json()
        updated = client.patch(
            f"/api/v1/tasks/{created['id']}",
            json={"title": "  Renamed  ", "description": ""},
        )

    assert updated.status_code == 200
    assert updated.json()["title"] == "Renamed"
    assert updated.json()["description"] == ""
    assert updated.json()["completed"] is False
    assert updated.json()["created_at"] == created["created_at"]
    assert updated.json()["updated_at"] >= created["updated_at"]


@pytest.mark.parametrize(
    ("method", "payload"),
    [
        ("get", None),
        ("delete", None),
        ("put", {"title": "Missing", "description": None, "completed": False}),
        ("patch", {"completed": True}),
    ],
)
def test_http_all_crud_operations_report_missing_resources(
    method: str, payload: dict[str, object] | None
) -> None:
    """All task-specific CRUD operations consistently translate a missing resource."""
    with make_client() as client:
        request = getattr(client, method)
        response = (
            request("/api/v1/tasks/42")
            if payload is None
            else request("/api/v1/tasks/42", json=payload)
        )

    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "task_not_found", "message": "Task 42 was not found."}
    }


def test_http_invalid_replacement_does_not_mutate_an_existing_task() -> None:
    """Validation failure on PUT leaves the existing task representation unchanged."""
    with make_client() as client:
        created = client.post(
            "/api/v1/tasks",
            json={"title": "Original", "description": "Retained", "completed": False},
        ).json()
        invalid = client.put(
            f"/api/v1/tasks/{created['id']}",
            json={"title": "Replacement", "completed": True},
        )
        fetched = client.get(f"/api/v1/tasks/{created['id']}")

    assert invalid.status_code == 422
    assert fetched.status_code == 200
    assert fetched.json() == created


def test_http_deleted_identifiers_are_not_reused() -> None:
    """Deletion removes the resource without resetting the local identifier sequence."""
    with make_client() as client:
        first = client.post("/api/v1/tasks", json={"title": "First"}).json()
        assert client.delete(f"/api/v1/tasks/{first['id']}").status_code == 204
        second = client.post("/api/v1/tasks", json={"title": "Second"}).json()
        after_delete = client.get(f"/api/v1/tasks/{first['id']}")

    assert second["id"] == 2
    assert after_delete.status_code == 404
