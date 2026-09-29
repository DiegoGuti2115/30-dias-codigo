"""Aplicación FastAPI local para el dashboard no clínico."""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.v1 import router as api_v1_router
from src.core.settings import get_settings
from src.repositories.local_fixture_repository import LocalFixtureDashboardRepository


def create_app() -> FastAPI:
    """Crea una API local con fixture sintético y límites de desarrollo seguros."""
    settings = get_settings()
    application = FastAPI(
        title="Health Dashboard API",
        description="API local no clínica para datos sintéticos del dashboard.",
        version="0.1.0",
    )
    application.state.dashboard_repository = LocalFixtureDashboardRepository(settings.fixture_path)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @application.exception_handler(HTTPException)
    async def http_exception_handler(_request: Request, error: HTTPException) -> JSONResponse:
        """Normaliza los errores de dominio sin exponer detalles internos."""
        if isinstance(error.detail, dict) and {"code", "message", "details"} <= error.detail.keys():
            return JSONResponse(status_code=error.status_code, content=error.detail)
        return JSONResponse(
            status_code=error.status_code,
            content={
                "code": "request_failed",
                "message": "La solicitud no se pudo completar.",
                "details": [],
            },
        )

    @application.exception_handler(RequestValidationError)
    async def request_validation_error_handler(
        _request: Request, error: RequestValidationError
    ) -> JSONResponse:
        """Devuelve errores de entrada estables sin reflejar valores enviados."""
        details = sorted({str(item["type"]) for item in error.errors()})
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "code": "invalid_request",
                "message": "La solicitud no cumple el formato requerido.",
                "details": details,
            },
        )

    application.include_router(api_v1_router)

    @application.get("/health", tags=["sistema"])
    def health_check() -> dict[str, str]:
        """Expone disponibilidad técnica sin información sensible."""
        return {"status": "ok"}

    return application


app = create_app()
