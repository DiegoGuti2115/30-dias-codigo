"""FastAPI transport layer for the public v1 upload-inspection contract.

The route performs multipart transport validation only. Filename validation,
streaming size enforcement, and fingerprint calculation remain delegated to the
pure Phase 4 inspection service.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Literal, cast

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from python_multipart.exceptions import MultipartParseError
from src.filename_validation import FilenameValidationError
from src.inspection import FileTooLargeError, inspect_file
from src.schemas import ErrorBody, ErrorDetail, ErrorResponse, InspectionResponse
from starlette.datastructures import FormData, UploadFile
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.formparsers import MultiPartException
from starlette.middleware.base import BaseHTTPMiddleware

CONTRACT_MEDIA_TYPE = "application/json; charset=utf-8"
INSPECT_PATH = "/api/v1/inspect"


class ContractJSONResponse(JSONResponse):
    """JSON response with the media type fixed by the public contract."""

    media_type = CONTRACT_MEDIA_TYPE


def _error_response(
    status_code: int,
    code: Literal[
        "malformed_multipart",
        "file_too_large",
        "unsupported_media_type",
        "validation_error",
        "method_not_allowed",
        "internal_error",
    ],
    message: str,
    details: list[ErrorDetail] | None = None,
) -> ContractJSONResponse:
    """Serialize an error using the public envelope without client input."""

    payload = ErrorResponse(
        error=ErrorBody(code=code, message=message, details=details or [])
    ).model_dump(mode="json")
    return ContractJSONResponse(status_code=status_code, content=payload)


def _validation_response(rule: str, message: str) -> ContractJSONResponse:
    """Return one safe, stable validation error for the multipart file field."""

    return _error_response(
        status_code=422,
        code="validation_error",
        message="La solicitud no cumple el contrato.",
        details=[ErrorDetail(field="file", rule=rule, message=message)],
    )


class MultipartContentTypeMiddleware(BaseHTTPMiddleware):
    """Reject unsupported media types before invoking multipart parsing."""

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Any]]
    ) -> ContractJSONResponse | Any:
        if request.method == "POST" and request.url.path == INSPECT_PATH:
            content_type = request.headers.get("content-type", "")
            media_type, _, parameters = content_type.partition(";")
            if media_type.strip().lower() != "multipart/form-data":
                return _error_response(
                    status_code=415,
                    code="unsupported_media_type",
                    message="La solicitud debe usar multipart/form-data.",
                )
            if "boundary=" not in parameters.lower():
                return _error_response(
                    status_code=400,
                    code="malformed_multipart",
                    message="El cuerpo multipart no puede interpretarse.",
                )
        return await call_next(request)


app = FastAPI(
    title="API de inspección de archivos",
    version="1.0.0",
    description="API local y sin estado para inspeccionar una única carga multipart.",
    default_response_class=ContractJSONResponse,
)
app.add_middleware(MultipartContentTypeMiddleware)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    _request: Request, exception: StarletteHTTPException
) -> ContractJSONResponse:
    """Translate public-route method and multipart parser errors safely."""

    if exception.status_code == 405:
        return _error_response(
            status_code=405,
            code="method_not_allowed",
            message="El método HTTP no está permitido para esta ruta.",
        )
    return _error_response(
        status_code=400,
        code="malformed_multipart",
        message="El cuerpo multipart no puede interpretarse.",
    )


@app.exception_handler(Exception)
async def unexpected_exception_handler(
    _request: Request, _exception: Exception
) -> ContractJSONResponse:
    """Prevent unexpected failures from exposing implementation details."""

    return _error_response(
        status_code=500,
        code="internal_error",
        message="Se produjo un error interno.",
    )


@app.post(
    INSPECT_PATH,
    response_model=InspectionResponse,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        415: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "required": ["file"],
                        "additionalProperties": False,
                        "properties": {"file": {"type": "string", "format": "binary"}},
                    }
                }
            },
        }
    },
)
async def inspect(request: Request) -> InspectionResponse | ContractJSONResponse:
    """Inspect exactly one multipart file without duplicating core inspection rules."""

    try:
        async with request.form(max_files=2, max_fields=2) as form:
            file_or_error = _single_file_or_error(form)
            if isinstance(file_or_error, ContractJSONResponse):
                return file_or_error

            if file_or_error.filename is None:
                return _validation_response(
                    "filename_required", "El archivo debe incluir un nombre válido."
                )

            try:
                return inspect_file(
                    cast(Any, file_or_error.file),
                    filename=file_or_error.filename,
                    media_type_declared=file_or_error.content_type,
                )
            except FilenameValidationError:
                return _validation_response(
                    "filename_invalid", "El nombre del archivo no cumple el contrato."
                )
            except FileTooLargeError:
                return _error_response(
                    status_code=413,
                    code="file_too_large",
                    message="El contenido del archivo supera el límite de 5 MiB.",
                    details=[
                        ErrorDetail(
                            field="file",
                            rule="max_size",
                            message="El archivo no puede superar 5 MiB.",
                        )
                    ],
                )
    except (MultiPartException, MultipartParseError):
        return _error_response(
            status_code=400,
            code="malformed_multipart",
            message="El cuerpo multipart no puede interpretarse.",
        )


def _single_file_or_error(form: FormData) -> UploadFile | ContractJSONResponse:
    """Enforce the multipart field cardinality and reject every extra field."""

    if any(field_name != "file" for field_name, _value in form.multi_items()):
        return _validation_response("extra_field", "No se permiten campos multipart adicionales.")

    uploaded_values = form.getlist("file")
    uploaded_files = [value for value in uploaded_values if isinstance(value, UploadFile)]
    if not uploaded_values:
        return _validation_response(
            "required", "Debe enviarse exactamente un archivo en el campo file."
        )
    if len(uploaded_values) != 1 or len(uploaded_files) != 1:
        return _validation_response(
            "exactly_one", "Debe enviarse exactamente un archivo en el campo file."
        )
    return uploaded_files[0]
