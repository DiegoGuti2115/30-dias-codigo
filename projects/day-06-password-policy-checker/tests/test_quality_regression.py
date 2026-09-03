"""Phase 5 regression checks for references, output, and versioned resources."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from policy import POLICY_V1
from reporters import INVALID_MESSAGE, VALID_MESSAGE, format_validation_result
from validator import validate_password

SCENARIO_CATALOG = PROJECT_ROOT / "data" / "fixtures" / "scenario-catalog.json"
SCENARIO_RESULTS = PROJECT_ROOT / "data" / "expected" / "scenario-results.json"


class QualityRegressionTests(unittest.TestCase):
    """Protect the Phase 5 public behavior without versioning passwords."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = cls._read_json(SCENARIO_CATALOG)
        cls.references = cls._read_json(SCENARIO_RESULTS)

    def test_every_catalog_scenario_has_one_complete_reference(self) -> None:
        scenario_ids = {scenario["id"] for scenario in self.catalog["scenarios"]}
        reference_ids = set(self.references["results"])

        self.assertEqual(scenario_ids, reference_ids)
        self.assertEqual(
            [rule.identifier for rule in POLICY_V1.rules], self.references["rule_order"]
        )
        for scenario_id, reference in self.references["results"].items():
            with self.subTest(scenario=scenario_id):
                self.assertIsInstance(reference["is_valid"], bool)
                self.assertEqual(5, len(reference["rules"]))
                self.assertTrue(all(isinstance(state, bool) for state in reference["rules"]))
                self.assertIsInstance(reference["has_whitespace"], bool)

    def test_formatter_matches_contractual_order_for_every_reference(self) -> None:
        messages = {rule.identifier: rule.failure_message for rule in POLICY_V1.rules}
        for scenario in self.catalog["scenarios"]:
            scenario_id = scenario["id"]
            reference = self.references["results"][scenario_id]
            result = validate_password(self._build_ephemeral_candidate(scenario))
            expected_lines = [VALID_MESSAGE if reference["is_valid"] else INVALID_MESSAGE]
            expected_lines.extend(
                messages[rule.identifier]
                for rule, is_satisfied in zip(POLICY_V1.rules, reference["rules"])
                if not is_satisfied
            )
            if reference["has_whitespace"]:
                expected_lines.append(POLICY_V1.whitespace_failure_message)

            with self.subTest(scenario=scenario_id):
                self.assertEqual("\n".join(expected_lines) + "\n", format_validation_result(result))

    def test_versioned_resources_describe_only_synthetic_conditions(self) -> None:
        resources = (
            SCENARIO_CATALOG,
            SCENARIO_RESULTS,
            PROJECT_ROOT / "docs" / "ESCENARIOS_FASE_2.md",
            PROJECT_ROOT / "docs" / "USO_SEGURO.md",
            PROJECT_ROOT / "examples" / "USO.md",
        )
        secret_assignment_markers = ("pass" + "word=", "contrase" + "ña=")
        for path in resources:
            with self.subTest(resource=path.relative_to(PROJECT_ROOT).as_posix()):
                content = path.read_text(encoding="utf-8").casefold()
                for marker in secret_assignment_markers:
                    self.assertNotIn(marker, content)

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _build_ephemeral_candidate(scenario: dict[str, Any]) -> str:
        category_characters = {
            "uppercase": chr(0x41),
            "lowercase": chr(0x61),
            "decimal-digit": chr(0x31),
            "special": chr(0x21),
            "unicode-uppercase": chr(0x00C4),
            "unicode-lowercase": chr(0x00DF),
            "unicode-decimal-digit": chr(0x0661),
            "combining-mark": chr(0x0301),
        }
        categories = scenario["categories"]
        value = "".join(category_characters[category] for category in categories)
        target_length = scenario["length"] - int(scenario["whitespace"])
        if len(value) < target_length:
            if "combining-mark" in categories:
                filler = category_characters["combining-mark"]
            elif "lowercase" in categories or "unicode-lowercase" in categories:
                filler = chr(0x61)
            else:
                filler = chr(0x41)
            value += filler * (target_length - len(value))
        if scenario["whitespace"]:
            value += chr(0x2003)
        return value


if __name__ == "__main__":
    unittest.main()
