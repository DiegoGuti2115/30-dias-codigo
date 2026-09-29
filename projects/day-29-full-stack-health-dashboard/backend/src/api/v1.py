"""Rutas HTTP v1 para la demo local y no clínica."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.domain.contracts import ErrorResponse, HealthDashboardFixture, Measurement, MeasurementCreate
from src.repositories.dashboard_repository import DashboardRepository
from src.repositories.local_fixture_repository import DashboardDataError

router = APIRouter(prefix="/api/v1", tags=["dashboard"])


def get_dashboard_repository(request: Request) -> DashboardRepository:
    """Obtiene el adaptador local registrado por la aplicación."""
    return request.app.state.dashboard_repository


DashboardRepositoryDependency = Annotated[DashboardRepository, Depends(get_dashboard_repository)]


@router.get(
    "/dashboard",
    response_model=HealthDashboardFixture,
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse}},
)
def get_dashboard(repository: DashboardRepositoryDependency) -> HealthDashboardFixture:
    """Devuelve datos sintéticos validados para el dashboard local."""
    try:
        return repository.load_dashboard()
    except DashboardDataError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "dashboard_unavailable",
                "message": "La fuente local del dashboard no está disponible.",
                "details": [],
            },
        ) from error


@router.post(
    "/measurements",
    response_model=Measurement,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {"model": ErrorResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse},
    },
)
def create_measurement(
    payload: MeasurementCreate, repository: DashboardRepositoryDependency
) -> Measurement:
    """Registra una medición manual solo durante la sesión local actual."""
    try:
        return repository.add_manual_measurement(payload)
    except KeyError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "metric_not_found",
                "message": "La métrica solicitada no está disponible.",
                "details": [],
            },
        ) from error
    except DashboardDataError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "dashboard_unavailable",
                "message": "La fuente local del dashboard no está disponible.",
                "details": [],
            },
        ) from error
