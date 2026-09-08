"""Phase 2 coverage for deterministic local fixture loading and validation."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

from pydantic import ValidationError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from fixtures import FixtureLoadError, load_fixture_catalog  # noqa: E402
from models import FixtureCatalog  # noqa: E402


FIXTURE_PATH = PROJECT_ROOT / "data" / "fixtures" / "portfolio-v1.json"


class FixtureLoadingTests(unittest.TestCase):
    """Verify valid local source data and controlled handling of invalid source data."""

    def setUp(self) -> None:
        self.payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    def test_catalog_loads_deterministically_with_synthetic_data(self) -> None:
        first = load_fixture_catalog(FIXTURE_PATH)
        second = load_fixture_catalog(FIXTURE_PATH)

        self.assertEqual(first.model_dump(mode="json"), second.model_dump(mode="json"))
        self.assertEqual(1, first.version)
        self.assertEqual("Jordan Vega", first.profile.name)
        self.assertTrue(first.profile_public)
        self.assertEqual(
            ["portfolio-api", "log-summary-tool", "draft-internal-notes"],
            [project.slug for project in first.projects],
        )

    def test_catalog_contains_only_contract_valid_records(self) -> None:
        catalog = load_fixture_catalog(FIXTURE_PATH)

        self.assertEqual("2026-09", catalog.projects[0].published_at)
        self.assertEqual("2023-09", catalog.experience[1].started_at)
        self.assertEqual("2024-06", catalog.experience[1].ended_at)
        self.assertEqual("https", catalog.profile.links[0].url.scheme)
        self.assertEqual(
            ["backend", "backend", "tools", "other"],
            [skill.category for skill in catalog.skills],
        )

    def test_duplicate_public_project_slug_is_rejected(self) -> None:
        duplicate = dict(self.payload["projects"][0])
        duplicate["title"] = "Duplicate slug"
        self.payload["projects"].append(duplicate)

        with self.assertRaisesRegex(ValidationError, "public project slugs must be unique"):
            FixtureCatalog.model_validate(self.payload)

    def test_duplicate_public_skill_category_and_name_is_rejected_ignoring_case(self) -> None:
        self.payload["skills"].append(
            {
                "public": True,
                "name": "python",
                "category": "backend",
            }
        )

        with self.assertRaisesRegex(ValidationError, "public skill category/name pairs must be unique"):
            FixtureCatalog.model_validate(self.payload)

    def test_invalid_month_url_and_experience_chronology_are_rejected(self) -> None:
        self.payload["projects"][0]["published_at"] = "2026-13"
        self.payload["profile"]["links"][0]["url"] = "ftp://invalid.example.test"
        self.payload["experience"][1]["ended_at"] = "2023-08"

        with self.assertRaises(ValidationError) as context:
            FixtureCatalog.model_validate(self.payload)

        messages = str(context.exception)
        self.assertIn("String should match pattern", messages)
        self.assertIn("URL scheme should be 'http' or 'https'", messages)
        self.assertIn("ended_at must be equal to or later than started_at", messages)

    def test_unknown_fields_are_rejected(self) -> None:
        self.payload["profile"]["private_note"] = "must not be accepted"

        with self.assertRaises(ValidationError) as context:
            FixtureCatalog.model_validate(self.payload)

        self.assertIn("Extra inputs are not permitted", str(context.exception))

    def test_invalid_json_and_missing_file_raise_controlled_load_errors(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            invalid_json = temporary_path / "invalid.json"
            invalid_json.write_text("{", encoding="utf-8")

            with self.assertRaisesRegex(FixtureLoadError, "not valid JSON"):
                load_fixture_catalog(invalid_json)

            with self.assertRaisesRegex(FixtureLoadError, "could not be read"):
                load_fixture_catalog(temporary_path / "missing.json")

    def test_contract_invalid_json_document_raises_controlled_load_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            invalid_catalog = Path(temporary_directory) / "invalid-catalog.json"
            self.payload["projects"][0]["slug"] = "Invalid_Slug"
            invalid_catalog.write_text(json.dumps(self.payload), encoding="utf-8")

            with self.assertRaisesRegex(FixtureLoadError, "does not satisfy the domain contract"):
                load_fixture_catalog(invalid_catalog)


if __name__ == "__main__":
    unittest.main()
