"""HTTP integration coverage for the local portfolio API, including Phase 5 hardening."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from main import create_app  # noqa: E402


FIXTURE_PATH = PROJECT_ROOT / "data" / "fixtures" / "portfolio-v1.json"


class PortfolioHttpApiTests(unittest.TestCase):
    """Verify Phase 4 routes, public projections, and controlled HTTP failures."""

    def setUp(self) -> None:
        self.client = TestClient(create_app(FIXTURE_PATH))

    def test_health_is_fixture_independent(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(200, response.status_code)
        self.assertEqual({"status": "ok"}, response.json())
        self.assertEqual("application/json", response.headers["content-type"])

    def test_public_resources_match_contract_order_and_hide_source_metadata(self) -> None:
        profile = self.client.get("/api/v1/profile")
        projects = self.client.get("/api/v1/projects")
        skills = self.client.get("/api/v1/skills")
        experience = self.client.get("/api/v1/experience")

        self.assertEqual(200, profile.status_code)
        self.assertEqual("Jordan Vega", profile.json()["name"])
        self.assertNotIn("public", profile.json())

        self.assertEqual(200, projects.status_code)
        project_items = projects.json()["items"]
        self.assertEqual(["portfolio-api", "log-summary-tool"], [item["slug"] for item in project_items])
        self.assertNotIn("description", project_items[0])
        self.assertNotIn("public", project_items[0])
        self.assertNotIn("links", project_items[1])
        self.assertEqual("2026-08", project_items[1]["published_at"])

        self.assertEqual(200, skills.status_code)
        skill_items = skills.json()["items"]
        self.assertEqual(["FastAPI", "Python", "Git"], [item["name"] for item in skill_items])
        self.assertNotIn("public", skill_items[0])
        self.assertNotIn("context", skill_items[1])

        self.assertEqual(200, experience.status_code)
        experience_items = experience.json()["items"]
        self.assertEqual(
            ["Sample Systems Lab", "Example Learning Institute"],
            [item["organization"] for item in experience_items],
        )
        self.assertNotIn("public", experience_items[0])
        self.assertNotIn("ended_at", experience_items[0])

    def test_project_detail_is_explicit_and_returns_controlled_absence(self) -> None:
        detail = self.client.get("/api/v1/projects/portfolio-api")
        missing = self.client.get("/api/v1/projects/not-found")
        private = self.client.get("/api/v1/projects/draft-internal-notes")

        self.assertEqual(200, detail.status_code)
        self.assertEqual("Portfolio API", detail.json()["title"])
        self.assertIn("description", detail.json())
        self.assertNotIn("public", detail.json())

        expected_error = {
            "error": {
                "code": "project_not_found",
                "message": "The requested public project was not found.",
            }
        }
        self.assertEqual(404, missing.status_code)
        self.assertEqual(expected_error, missing.json())
        self.assertEqual(404, private.status_code)
        self.assertEqual(expected_error, private.json())

    def test_slug_validation_enforces_invalid_forms_and_length_boundaries(self) -> None:
        for invalid_slug in ("Portfolio-API", "-portfolio", "portfolio-", "portfolio--api", "a" * 81):
            with self.subTest(invalid_slug=invalid_slug):
                response = self.client.get(f"/api/v1/projects/{invalid_slug}")

                self.assertEqual(422, response.status_code)
                self.assertEqual("application/json", response.headers["content-type"])
                body = response.json()
                self.assertIsInstance(body["detail"], list)
                self.assertEqual(["path", "slug"], body["detail"][0]["loc"])
                self.assertIn("type", body["detail"][0])

        maximum_length_slug = "a" * 80
        response = self.client.get(f"/api/v1/projects/{maximum_length_slug}")

        self.assertEqual(404, response.status_code)
        self.assertEqual("project_not_found", response.json()["error"]["code"])

    def test_invalid_source_returns_safe_500_while_health_remains_available(self) -> None:
        client = TestClient(create_app(Path("missing-fixture.json")))

        self.assertEqual({"status": "ok"}, client.get("/health").json())
        response = client.get("/api/v1/profile")

        self.assertEqual(500, response.status_code)
        self.assertEqual(
            {
                "error": {
                    "code": "internal_error",
                    "message": "An unexpected error occurred.",
                }
            },
            response.json(),
        )

    def test_unexpected_failures_use_the_safe_500_contract(self) -> None:
        app = create_app(FIXTURE_PATH)
        app.state.portfolio_service = _FailingProfileService()
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/api/v1/profile")

        self.assertEqual(500, response.status_code)
        self.assertEqual(
            {
                "error": {
                    "code": "internal_error",
                    "message": "An unexpected error occurred.",
                }
            },
            response.json(),
        )

    def test_public_json_never_leaks_private_fixture_records_or_source_metadata(self) -> None:
        public_paths = (
            "/api/v1/profile",
            "/api/v1/projects",
            "/api/v1/projects/portfolio-api",
            "/api/v1/skills",
            "/api/v1/experience",
        )
        private_source_markers = (
            "Draft Internal Notes",
            "Private Practice Group",
            "Internal Planning",
            "source-only record",
        )

        for path in public_paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                serialized = response.text

                self.assertEqual(200, response.status_code)
                self.assertNotIn('"public"', serialized)
                self.assertNotIn('"profile_public"', serialized)
                self.assertNotIn("null", serialized)
                for marker in private_source_markers:
                    self.assertNotIn(marker, serialized)

    def test_read_only_contract_rejects_writes_and_openapi_declares_only_get_routes(self) -> None:
        paths = (
            "/health",
            "/api/v1/profile",
            "/api/v1/projects",
            "/api/v1/projects/portfolio-api",
            "/api/v1/skills",
            "/api/v1/experience",
        )
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(405, self.client.post(path, json={}).status_code)

        document = self.client.get("/openapi.json")

        self.assertEqual(200, document.status_code)
        self.assertEqual(
            {"get"},
            {method for operations in document.json()["paths"].values() for method in operations},
        )

    def test_create_app_uses_the_fixture_path_given_to_that_instance(self) -> None:
        payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        payload["profile"]["name"] = "Isolated Fixture Profile"

        with tempfile.TemporaryDirectory() as temporary_directory:
            custom_fixture = Path(temporary_directory) / "portfolio.json"
            custom_fixture.write_text(json.dumps(payload), encoding="utf-8")
            isolated_client = TestClient(create_app(custom_fixture))

            response = isolated_client.get("/api/v1/profile")

        self.assertEqual(200, response.status_code)
        self.assertEqual("Isolated Fixture Profile", response.json()["name"])
        self.assertEqual("Jordan Vega", self.client.get("/api/v1/profile").json()["name"])


class _FailingProfileService:
    """Minimal double used to verify the public unexpected-error boundary."""

    def get_profile(self) -> object:
        raise RuntimeError("must not be exposed to HTTP clients")


if __name__ == "__main__":
    unittest.main()
