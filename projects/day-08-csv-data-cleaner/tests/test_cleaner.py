from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cleaner import clean_dataset
from csv_profile import CsvContractError, load_csv
from plan import load_plan


FIXTURES = PROJECT_ROOT / "data" / "fixtures"
EXPECTED = PROJECT_ROOT / "data" / "expected"


class CleanerTests(unittest.TestCase):
    def test_happy_path_matches_phase_two_csv_and_summary_references(self) -> None:
        result = clean_dataset(
            load_csv(FIXTURES / "happy-input.csv"),
            load_plan(FIXTURES / "plan-all-operations.json"),
        )

        self.assertEqual(result.headers, ("Display Name", "status", "comment"))
        self.assertEqual(result.rows, (("Ana", "", "=demo"), ("Ben", "", "ready"), ("Cia", "", "note")))
        self.assertEqual(result.summary(), json.loads((EXPECTED / "happy-summary.json").read_text(encoding="utf-8")))
        self.assertEqual(
            "\n".join([",".join(result.headers), *[",".join(row) for row in result.rows]]) + "\n",
            (EXPECTED / "happy-cleaned.csv").read_text(encoding="utf-8"),
        )

    def test_no_change_plan_matches_reference(self) -> None:
        result = clean_dataset(
            load_csv(FIXTURES / "no-changes-input.csv"),
            load_plan(FIXTURES / "plan-no-changes.json"),
        )

        self.assertEqual(result.summary(), json.loads((EXPECTED / "no-changes-summary.json").read_text(encoding="utf-8")))

    def test_normalization_collision_is_rejected_before_transforming(self) -> None:
        dataset = load_csv(FIXTURES / "header-collision-input.csv")
        plan = load_plan(FIXTURES / "plan-normalize-headers.json")

        with self.assertRaisesRegex(CsvContractError, "header_normalization_collision"):
            clean_dataset(dataset, plan)
