from __future__ import annotations

from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from plan import PlanValidationError, load_plan, parse_plan


FIXTURES = PROJECT_ROOT / "data" / "fixtures"


class PlanTests(unittest.TestCase):
    def test_normalizes_declared_operations_to_contractual_order(self) -> None:
        plan = load_plan(FIXTURES / "plan-all-operations.json")

        self.assertEqual(plan.version, 1)
        self.assertEqual(plan.requested_operations, (
            "normalize_headers",
            "drop_empty_rows",
            "trim_fields",
            "replace_missing_markers",
            "drop_exact_duplicates",
        ))
        self.assertEqual(plan.operations[3].markers, ("N/A", "NULL"))

    def test_rejects_phase_two_invalid_plan_fixtures(self) -> None:
        cases = {
            "invalid-plan-extra-root.json": "plan_extra_root_key",
            "invalid-plan-unknown-operation.json": "plan_unknown_operation",
            "invalid-plan-duplicate-operation.json": "plan_duplicate_operation",
            "invalid-plan-empty-markers.json": "plan_invalid_markers",
            "invalid-plan-version.json": "plan_unsupported_version",
        }
        for fixture, code in cases.items():
            with self.subTest(fixture=fixture):
                with self.assertRaisesRegex(PlanValidationError, code):
                    load_plan(FIXTURES / fixture)

    def test_rejects_boolean_version_and_unknown_operation_keys(self) -> None:
        with self.assertRaisesRegex(PlanValidationError, "plan_unsupported_version"):
            parse_plan({"version": True, "operations": [{"operation": "trim_fields"}]})
        with self.assertRaisesRegex(PlanValidationError, "plan_invalid_operation_keys"):
            parse_plan({"version": 1, "operations": [{"operation": "trim_fields", "extra": True}]})
