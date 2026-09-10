"""FastAPI transport layer for the public v1 text-analysis contract."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Literal

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from src.analyzer import analyze_text
from src.schemas import AnalyzeRequest, AnalyzeResponse, ErrorBody, ErrorDetail, ErrorResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

JSON_MEDIA_TYPE = "application/json"
CONTRACT_MEDIA_TYPE = "application/json; charset=utf-8"


class ContractJSONResponse(JSONResponse):
    """JSON response with the UTF-8 media type specified by the public contract."""

    media_type = CONTRACT_MEDIA_TYPE


def _error_response(
    status_code: int,
    code: Literal[
        "invalid_json",
        "unsupported_media_type",
        "validation_error",
        "method_not_allowed",
        "internal_error",
    ],
    message: str,
    details: list[ErrorDetail] | None = None,
) -> ContractJSONResponse:
    """Serialize an error using the single public response shape."""

    payload = ErrorResponse(
        error=ErrorBody(code=code, message=message, details=details or [])
    ).model_dump(mode="json")
    return ContractJSONResponse(status_code=status_code, content=payload)


class ContentTypeMiddleware(BaseHTTPMiddleware):
    """Reject non-JSON requests for the only public operation before validation."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Any]]
    ) -> ContractJSONResponse | Any:
        if request.method == "POST" and request.url.path == "/api/v1/analyze":
            content_type = request.headers.get("content-type", "")
            if content_type.split(";", maxsplit=1)[0].strip().lower() != JSON_MEDIA_TYPE:
                return _error_response(
                    status_code=415,
                    code="unsupported_media_type",
                    message="La solicitud debe usar application/json.",
                    details=[],
                )
        return await call_next(request)


def _validation_detail(error: dict[str, Any]) -> ErrorDetail:
    """Translate one FastAPI/Pydantic validation error to the stable public detail."""

    error_type = str(error["type"])
    location = error.get("loc", ())
    field = str(location[-1]) if location and location[-1] != "body" else "body"

    if error_type == "json_invalid":
        return ErrorDetail(
            field="body",
            rule="invalid_json",
            message="El cuerpo no puede interpretarse como JSON.",
        )

    rule_and_message = {
        "missing": ("required", "text es obligatorio."),
        "string_too_short": ("min_length", "text debe contener al menos 1 carácter."),
        "string_too_long": ("max_length", "text no puede superar 10.000 caracteres."),
        "string_type": ("string_type", "text debe ser una cadena."),
        "extra_forbidden": ("extra_field", "La propiedad no está permitida."),
    }
    rule, message = rule_and_message.get(
        error_type, ("invalid", "La solicitud no cumple el contrato.")
    )
    if error_type == "missing":
        field = "text"

    return ErrorDetail(field=field, rule=rule, message=message)


app = FastAPI(
    title="API de análisis de texto",
    version="1.0.0",
    description="API local y determinista para métricas, frecuencias y palabras clave.",
    default_response_class=ContractJSONResponse,
)
app.add_middleware(ContentTypeMiddleware)


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    _request: Request, exception: RequestValidationError
) -> ContractJSONResponse:
    """Return contract errors for malformed JSON and schema validation failures."""

    details = [_validation_detail(error) for error in exception.errors()]
    if any(detail.rule == "invalid_json" for detail in details):
        return _error_response(
            status_code=400,
            code="invalid_json",
            message="El cuerpo no puede interpretarse como JSON.",
            details=details,
        )
    return _error_response(
        status_code=422,
        code="validation_error",
        message="La solicitud no cumple el contrato.",
        details=details,
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    _request: Request, exception: StarletteHTTPException
) -> ContractJSONResponse:
    """Translate method mismatches for the public route to the documented error."""

    if exception.status_code == 405:
        return _error_response(
            status_code=405,
            code="method_not_allowed",
            message="El método HTTP no está permitido para esta ruta.",
            details=[],
        )
    return _error_response(
        status_code=exception.status_code,
        code="internal_error",
        message="La solicitud no puede completarse.",
        details=[],
    )


@app.exception_handler(Exception)
async def unexpected_exception_handler(
    _request: Request, _exception: Exception
) -> ContractJSONResponse:
    """Prevent unexpected server failures from exposing internal implementation details."""

    return _error_response(
        status_code=500,
        code="internal_error",
        message="Se produjo un error interno.",
        details=[],
    )


@app.post("/api/v1/analyze", response_model=AnalyzeResponse, status_code=200)
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze one validated text independently of all other requests."""

    return analyze_text(request.text)
