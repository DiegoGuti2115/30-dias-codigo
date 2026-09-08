"""Loading and validation for the deterministic local portfolio fixture catalog.

The module deliberately stops at loading and domain validation. Query services,
collection ordering, HTTP routes, and response projection begin in later phases.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from models import FixtureCatalog


class FixtureLoadError(ValueError):
    """Raised when the local fixture source cannot be decoded or validated safely."""


def load_fixture_catalog(path: Path) -> FixtureCatalog:
    """Load one UTF-8 JSON catalog and return its fully validated domain model."""
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as error:
        raise FixtureLoadError("fixture catalog could not be read") from error

    try:
        payload = json.loads(source)
    except json.JSONDecodeError as error:
        raise FixtureLoadError("fixture catalog is not valid JSON") from error

    try:
        return FixtureCatalog.model_validate(payload)
    except ValidationError as error:
        raise FixtureLoadError("fixture catalog does not satisfy the domain contract") from error
