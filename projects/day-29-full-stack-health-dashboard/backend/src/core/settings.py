"""Configuración local tipada y libre de secretos para la API."""

from dataclasses import dataclass
from functools import lru_cache
from os import getenv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CORS_ORIGIN = "http://localhost:3000"


@dataclass(frozen=True)
class Settings:
    """Valores de ejecución usados por adaptadores de la API local."""

    app_env: str
    cors_origins: tuple[str, ...]
    fixture_path: Path


def parse_cors_origins(raw_origins: str) -> tuple[str, ...]:
    """Convierte una lista separada por comas y rechaza comodines inseguros."""
    origins = tuple(origin.strip().rstrip("/") for origin in raw_origins.split(",") if origin.strip())
    if not origins:
        return (DEFAULT_CORS_ORIGIN,)
    if "*" in origins:
        raise ValueError("CORS_ORIGINS cannot include wildcard origins")
    return origins


@lru_cache
def get_settings() -> Settings:
    """Carga configuración de entorno con valores locales seguros por defecto."""
    return Settings(
        app_env=getenv("APP_ENV", "development"),
        cors_origins=parse_cors_origins(getenv("CORS_ORIGINS", DEFAULT_CORS_ORIGIN)),
        fixture_path=PROJECT_ROOT / "data" / "fixtures" / "health-dashboard.sample.json",
    )
