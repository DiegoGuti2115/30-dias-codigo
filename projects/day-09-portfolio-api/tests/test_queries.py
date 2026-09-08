"""Phase 3 coverage for local portfolio repository and read-only query services."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from errors import FixtureSourceError, ProjectNotFoundError  # noqa: E402
from repository import FixtureRepository  # noqa: E402
from services import PortfolioQueryService  # noqa: E402


FIXTURE_PATH = PROJECT_ROOT / "data" / "fixtures" / "portfolio-v1.json"


class PortfolioQueryServiceTests(unittest.TestCase):
    """Verify public visibility, deterministic ordering, and controlled source failures."""

    def setUp(self) -> None:
        self.repository = FixtureRepository(FIXTURE_PATH)
        self.service = PortfolioQueryService(self.repository)

    def test_profile_is_loaded_from_the_validated_public_catalog(self) -> None:
        profile = self.service.get_profile()

        self.assertEqual("Jordan Vega", profile.name)
        self.assertEqual("Backend developer focused on reliable APIs", profile.headline)

    def test_queries_filter_private_records_and_preserve_source_entities(self) -> None:
        catalog = self.repository.get_catalog()
        original_source = catalog.model_dump(mode="json")

        projects = self.service.list_projects()
        skills = self.service.list_skills()
        experience = self.service.list_experience()

        self.assertEqual(["portfolio-api", "log-summary-tool"], [item.slug for item in projects])
        self.assertEqual(["FastAPI", "Python", "Git"], [item.name for item in skills])
        self.assertEqual(
            ["Sample Systems Lab", "Example Learning Institute"],
            [item.organization for item in experience],
        )
        self.assertEqual(original_source, catalog.model_dump(mode="json"))
        self.assertEqual(3, len(self.repository.get_projects()))
        self.assertEqual(4, len(self.repository.get_skills()))
        self.assertEqual(3, len(self.repository.get_experience()))

    def test_project_detail_uses_exact_public_slug_and_hides_private_records(self) -> None:
        project = self.service.get_project_by_slug("portfolio-api")

        self.assertEqual("Portfolio API", project.title)
        self.assertEqual("portfolio-api", project.slug)
        with self.assertRaises(ProjectNotFoundError) as missing:
            self.service.get_project_by_slug("draft-internal-notes")
        self.assertEqual("draft-internal-notes", missing.exception.slug)
        self.assertEqual("public project was not found", str(missing.exception))

        with self.assertRaises(ProjectNotFoundError):
            self.service.get_project_by_slug("PORTFOLIO-API")

    def test_repository_loads_once_and_translates_fixture_errors(self) -> None:
        first = self.repository.get_catalog()
        FIXTURE_PATH.read_text(encoding="utf-8")
        second = self.repository.get_catalog()

        self.assertIs(first, second)
        with tempfile.TemporaryDirectory() as temporary_directory:
            unavailable = FixtureRepository(Path(temporary_directory) / "missing.json")
            with self.assertRaisesRegex(FixtureSourceError, "source is unavailable"):
                unavailable.get_catalog()

    def test_collection_ordering_follows_all_contract_tie_breakers(self) -> None:
        payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        payload["projects"] = [
            _project("undated", False, None),
            _project("dated-b", False, "2025-01"),
            _project("featured-older", True, "2024-01"),
            _project("dated-a", False, "2025-01"),
        ]
        payload["skills"] = [
            {"public": True, "name": "Zulu", "category": "tools"},
            {"public": True, "name": "Beta", "category": "backend"},
            {"public": True, "name": "Alpha", "category": "backend"},
        ]
        payload["experience"] = [
            _experience("Zeta Org", "Role B", "2025-01", "2025-02"),
            _experience("Alpha Org", "Role C", "2025-01", "2025-02"),
            _experience("Current Org", "Role A", "2025-01", None),
            _experience("Older Org", "Role A", "2024-12", None),
        ]

        service = _service_from_payload(payload)

        self.assertEqual(
            ["featured-older", "dated-a", "dated-b", "undated"],
            [item.slug for item in service.list_projects()],
        )
        self.assertEqual(["Alpha", "Beta", "Zulu"], [item.name for item in service.list_skills()])
        self.assertEqual(
            ["Current Org", "Alpha Org", "Zeta Org", "Older Org"],
            [item.organization for item in service.list_experience()],
        )


def _service_from_payload(payload: dict[str, object]) -> PortfolioQueryService:
    with tempfile.TemporaryDirectory() as temporary_directory:
        path = Path(temporary_directory) / "portfolio.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        repository = FixtureRepository(path)
        repository.get_catalog()
        return PortfolioQueryService(repository)


def _project(slug: str, featured: bool, published_at: str | None) -> dict[str, object]:
    project: dict[str, object] = {
        "public": True,
        "slug": slug,
        "title": slug,
        "summary": "Deterministic ordering test project.",
        "description": "Synthetic project used only to test ordering rules.",
        "technologies": ["Python"],
        "status": "completed",
        "featured": featured,
    }
    if published_at is not None:
        project["published_at"] = published_at
    return project


def _experience(
    organization: str, role: str, started_at: str, ended_at: str | None
) -> dict[str, object]:
    experience: dict[str, object] = {
        "public": True,
        "organization": organization,
        "role": role,
        "summary": "Synthetic experience used only to test ordering rules.",
        "started_at": started_at,
    }
    if ended_at is not None:
        experience["ended_at"] = ended_at
    return experience


if __name__ == "__main__":
    unittest.main()
