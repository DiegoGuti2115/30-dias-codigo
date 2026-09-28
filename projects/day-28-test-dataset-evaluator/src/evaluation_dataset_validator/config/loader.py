"""Carga y validación de archivos JSON de configuración locales."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError as PydanticValidationError

from evaluation_dataset_validator.config.settings import ValidationSettings
from evaluation_dataset_validator.errors import FileAccessError, InvalidConfigurationError


def load_validation_settings(source: Path) -> ValidationSettings:
    """Load a JSON configuration file into validated domain settings."""
    try:
        raw_content = source.read_text(encoding="utf-8")
    except OSError as error:
        raise FileAccessError(source) from error

    try:
        payload = json.loads(raw_content)
    except json.JSONDecodeError as error:
        raise InvalidConfigurationError(source, f"JSON inválido: {_json_detail(error)}") from error

    if not isinstance(payload, dict):
        raise InvalidConfigurationError(source, "la raíz debe ser un objeto JSON")

    try:
        return ValidationSettings.model_validate(payload)
    except PydanticValidationError as error:
        raise InvalidConfigurationError(source, _validation_detail(error)) from error


def _json_detail(error: json.JSONDecodeError) -> str:
    """Return a concise position-aware diagnostic for malformed JSON."""
    return f"{error.msg} (línea {error.lineno}, columna {error.colno})"


def _validation_detail(error: PydanticValidationError) -> str:
    """Return the first Pydantic issue without leaking an implementation traceback."""
    issue = error.errors()[0]
    location = ".".join(str(part) for part in issue["loc"])
    return f"{location}: {issue['msg']}"
