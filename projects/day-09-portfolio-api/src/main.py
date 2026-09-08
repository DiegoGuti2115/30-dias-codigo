"""FastAPI composition root for the local, read-only portfolio API v1."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, Path as PathParameter, Request
from fastapi.responses import JSONResponse

from errors import FixtureSourceError, PortfolioQueryError, ProjectNotFoundError
from repository import FixtureRepository
from schemas import (
    ErrorResponse,
    ExperienceListResponse,
    HealthResponse,
    ProfileResponse,
    ProjectDetailResponse,
    ProjectListResponse,
    SkillListResponse,
    experience_from_domain,
    profile_from_domain,
    project_detail_from_domain,
    project_summary_from_domain,
    skill_from_domain,
)
from services import PortfolioQueryService


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE_PATH = PROJECT_ROOT / "data" / "fixtures" / "portfolio-v1.json"
SLUG_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"


def create_app(fixture_path: Path = DEFAULT_FIXTURE_PATH) -> FastAPI:
    """Create an isolated application backed by one deterministic local fixture source."""
    repository = FixtureRepository(fixture_path)
    service = PortfolioQueryService(repository)
    app = FastAPI(title="Portfolio API", version="1.0.0")
    app.state.portfolio_service = service

    @app.exception_handler(ProjectNotFoundError)
    async def project_not_found_handler(
        request: Request, error: ProjectNotFoundError
    ) -> JSONResponse:
        """Map public-project absence to the stable v1 error response."""
        del request, error
        return JSONResponse(
            status_code=404,
            content=ErrorResponse(
                error={
                    "code": "project_not_found",
                    "message": "The requested public project was not found.",
                }
            ).model_dump(mode="json"),
        )

    @app.exception_handler(FixtureSourceError)
    async def fixture_source_handler(request: Request, error: FixtureSourceError) -> JSONResponse:
        """Map controlled fixture-source failure to a safe internal error response."""
        del request, error
        return _internal_error_response()

    @app.exception_handler(PortfolioQueryError)
    async def query_error_handler(request: Request, error: PortfolioQueryError) -> JSONResponse:
        """Ensure future controlled query failures never leak internal details."""
        del request, error
        return _internal_error_response()

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, error: Exception) -> JSONResponse:
        """Keep unanticipated application failures within the contract-defined 500 shape."""
        del request, error
        return _internal_error_response()

    def get_service() -> PortfolioQueryService:
        """Provide the phase-3 service without letting routes access fixtures directly."""
        return app.state.portfolio_service

    service_dependency = Depends(get_service)

    @app.get("/health", response_model=HealthResponse)
    def health_check() -> HealthResponse:
        """Provide the contract's fixture-independent minimal health response."""
        return HealthResponse(status="ok")

    @app.get("/api/v1/profile", response_model=ProfileResponse, response_model_exclude_none=True)
    def get_profile(service: PortfolioQueryService = service_dependency) -> ProfileResponse:
        """Return the only public profile through its explicit public projection."""
        return profile_from_domain(service.get_profile())

    @app.get(
        "/api/v1/projects",
        response_model=ProjectListResponse,
        response_model_exclude_none=True,
    )
    def list_projects(service: PortfolioQueryService = service_dependency) -> ProjectListResponse:
        """Return the full ordered public project collection without filters."""
        return ProjectListResponse(
            items=[project_summary_from_domain(project) for project in service.list_projects()]
        )

    @app.get(
        "/api/v1/projects/{slug}",
        response_model=ProjectDetailResponse,
        response_model_exclude_none=True,
        responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    )
    def get_project(
        slug: Annotated[
            str,
            PathParameter(min_length=1, max_length=80, pattern=SLUG_PATTERN),
        ],
        service: PortfolioQueryService = service_dependency,
    ) -> ProjectDetailResponse:
        """Return one exact-match public project detail or a controlled absence error."""
        return project_detail_from_domain(service.get_project_by_slug(slug))

    @app.get(
        "/api/v1/skills",
        response_model=SkillListResponse,
        response_model_exclude_none=True,
    )
    def list_skills(service: PortfolioQueryService = service_dependency) -> SkillListResponse:
        """Return the full ordered public skill collection without filters."""
        return SkillListResponse(items=[skill_from_domain(skill) for skill in service.list_skills()])

    @app.get(
        "/api/v1/experience",
        response_model=ExperienceListResponse,
        response_model_exclude_none=True,
    )
    def list_experience(service: PortfolioQueryService = service_dependency) -> ExperienceListResponse:
        """Return the full ordered public experience collection without filters."""
        return ExperienceListResponse(
            items=[experience_from_domain(entry) for entry in service.list_experience()]
        )

    return app


def _internal_error_response() -> JSONResponse:
    """Build the contract-defined 500 payload without exception details."""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error={
                "code": "internal_error",
                "message": "An unexpected error occurred.",
            }
        ).model_dump(mode="json"),
    )


app = create_app()
