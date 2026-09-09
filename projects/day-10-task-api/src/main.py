"""FastAPI application exposing the version 1 task CRUD contract."""

from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, Path, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.errors import TaskNotFoundError
from src.schemas import TaskCreate, TaskList, TaskRead, TaskReplace, TaskUpdate
from src.service import TaskService

ApiError = dict[str, dict[str, object]]
TaskId = Annotated[int, Path(gt=0, description="Positive task identifier")]


def error_response(status_code: int, code: str, message: str) -> JSONResponse:
    """Create the stable application-error response declared by the contract."""
    payload: ApiError = {"error": {"code": code, "message": message}}
    return JSONResponse(status_code=status_code, content=payload)


def create_app(service: TaskService | None = None) -> FastAPI:
    """Build an application with one isolated local task service instance."""
    application = FastAPI(
        title="API CRUD de tareas",
        version="1.0.0",
        description="API local para crear y administrar tareas.",
    )
    application.state.task_service = service or TaskService()

    @application.exception_handler(TaskNotFoundError)
    async def handle_task_not_found(_: Request, exc: TaskNotFoundError) -> JSONResponse:
        return error_response(
            status.HTTP_404_NOT_FOUND,
            "task_not_found",
            f"Task {exc.task_id} was not found.",
        )

    @application.exception_handler(StarletteHTTPException)
    async def handle_http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        if exc.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            return error_response(
                status.HTTP_405_METHOD_NOT_ALLOWED,
                "method_not_allowed",
                "The requested method is not allowed for this resource.",
            )
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @application.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        if request.method == "PATCH" and request.url.path.startswith("/api/v1/tasks/"):
            if any(
                "at least one editable field is required" in str(error.get("msg", ""))
                for error in exc.errors()
            ):
                return error_response(
                    status.HTTP_400_BAD_REQUEST,
                    "invalid_request",
                    "At least one editable field is required.",
                )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=jsonable_encoder({"detail": exc.errors()}),
        )

    @application.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, __: Exception) -> JSONResponse:
        return error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "internal_error",
            "An unexpected internal error occurred.",
        )

    def get_service(request: Request) -> TaskService:
        return request.app.state.task_service  # type: ignore[no-any-return]

    @application.post(
        "/api/v1/tasks",
        response_model=TaskRead,
        status_code=status.HTTP_201_CREATED,
        tags=["tasks"],
    )
    def create_task(payload: TaskCreate, request: Request) -> TaskRead:
        return get_service(request).create(payload)

    @application.get("/api/v1/tasks", response_model=TaskList, tags=["tasks"])
    def list_tasks(request: Request) -> TaskList:
        return get_service(request).list()

    @application.get("/api/v1/tasks/{task_id}", response_model=TaskRead, tags=["tasks"])
    def get_task(task_id: TaskId, request: Request) -> TaskRead:
        return get_service(request).get(task_id)

    @application.put("/api/v1/tasks/{task_id}", response_model=TaskRead, tags=["tasks"])
    def replace_task(task_id: TaskId, payload: TaskReplace, request: Request) -> TaskRead:
        return get_service(request).replace(task_id, payload)

    @application.patch("/api/v1/tasks/{task_id}", response_model=TaskRead, tags=["tasks"])
    def update_task(task_id: TaskId, payload: TaskUpdate, request: Request) -> TaskRead:
        return get_service(request).update(task_id, payload)

    @application.delete("/api/v1/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
    def delete_task(task_id: TaskId, request: Request) -> Response:
        get_service(request).delete(task_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return application


app = create_app()
