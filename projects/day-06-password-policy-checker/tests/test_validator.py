"""Reference-driven tests for the secret-free, deterministic policy v1 evaluator."""

from __future__ import annotations

import json
import sys
import unittest
from dataclasses import fields
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from policy import POLICY_V1
from validator import INVALID_PASSWORD_TYPE_MESSAGE, validate_password

SCENARIO_CATALOG = PROJECT_ROOT / "data" / "fixtures" / "scenario-catalog.json"
SCENARIO_RESULTS = PROJECT_ROOT / "data" / "expected" / "scenario-results.json"


class ValidationTests(unittest.TestCase):
    """Verify every non-sensitive Phase 2 reference using ephemeral inputs."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = cls._read_json(SCENARIO_CATALOG)
        cls.references = cls._read_json(SCENARIO_RESULTS)

    def test_policy_is_immutable_and_exposes_contractual_rule_order(self) -> None:
        self.assertEqual(POLICY_V1.minimum_length, 12)
        self.assertEqual(POLICY_V1.maximum_length, 128)
        self.assertEqual(
            tuple(rule.identifier for rule in POLICY_V1.rules),
            tuple(self.references["rule_order"]),
        )
        with self.assertRaisesRegex(AttributeError, "cannot assign to field"):
            POLICY_V1.minimum_length = 1  # type: ignore[misc]

    def test_synthetic_catalog_matches_every_structured_reference(self) -> None:
        for scenario in self.catalog["scenarios"]:
            scenario_id = scenario["id"]
            reference = self.references["results"][scenario_id]
            candidate = self._build_ephemeral_candidate(scenario)

            with self.subTest(scenario=scenario_id):
                result = validate_password(candidate)
                self.assertEqual(result.is_valid, reference["is_valid"])
                self.assertEqual(self._rule_states(result), tuple(reference["rules"]))
                self.assertEqual(result.has_whitespace, reference["has_whitespace"])

    def test_repeated_evaluation_is_deterministic_and_complete(self) -> None:
        scenario = self._scenario("combined-failures")
        candidate = self._build_ephemeral_candidate(scenario)

        first = validate_password(candidate)
        second = validate_password(candidate)

        self.assertEqual(first, second)
        self.assertEqual(
            tuple(rule.identifier for rule in first.rules),
            tuple(self.references["rule_order"]),
        )
        self.assertEqual(len(first.rules), 5)

    def test_non_text_input_raises_a_static_safe_error(self) -> None:
        for value in (None, 0, bytes(), []):
            with self.subTest(value_type=type(value).__name__):
                with self.assertRaisesRegex(TypeError, INVALID_PASSWORD_TYPE_MESSAGE):
                    validate_password(value)  # type: ignore[arg-type]

    def test_result_never_retains_the_evaluated_input_or_exact_length(self) -> None:
        candidate = self._build_ephemeral_candidate(self._scenario("all-rules-satisfied"))
        result = validate_password(candidate)

        retained_values = tuple(
            value
            for item in (result, *result.rules)
            for field in fields(item)
            if isinstance(value := getattr(item, field.name), (str, int))
        )
        self.assertNotIn(candidate, retained_values)
        self.assertNotIn(len(candidate), retained_values)

    @classmethod
    def _scenario(cls, scenario_id: str) -> dict[str, Any]:
        return next(
            scenario
            for scenario in cls.catalog["scenarios"]
            if scenario["id"] == scenario_id
        )

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

    @staticmethod
    def _rule_states(result: object) -> tuple[bool, ...]:
        return tuple(rule.is_satisfied for rule in result.rules)  # type: ignore[attr-defined]


if __name__ == "__main__":
    unittest.main()
