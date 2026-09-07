from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
FIXTURES = PROJECT_ROOT / "data" / "fixtures"
EXPECTED = PROJECT_ROOT / "data" / "expected"
sys.path.insert(0, str(SRC))

from cleaner import clean_dataset
from csv_profile import load_csv
from output import ExecutionPaths, PublicationError, publish_result
from plan import load_plan


class CliIntegrationTests(unittest.TestCase):
    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SRC / "main.py"), *arguments],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

    def test_happy_path_publishes_reference_artifacts_and_preserves_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            source = workspace / "happy-input.csv"
            plan = workspace / "plan.json"
            output_csv = workspace / "cleaned.csv"
            summary = workspace / "summary.json"
            source.write_bytes((FIXTURES / "happy-input.csv").read_bytes())
            plan.write_bytes((FIXTURES / "plan-all-operations.json").read_bytes())
            source_before = source.read_bytes()

            completed = self.run_cli("clean", str(source), str(plan), str(output_csv), str(summary))

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(completed.stderr, "")
            self.assertIn("Created cleaned CSV: cleaned.csv", completed.stdout)
            self.assertIn("Created summary JSON: summary.json", completed.stdout)
            self.assertNotIn(str(workspace), completed.stdout)
            self.assertEqual(source.read_bytes(), source_before)
            self.assertEqual(output_csv.read_bytes(), (EXPECTED / "happy-cleaned.csv").read_bytes())
            self.assertEqual(
                json.loads(summary.read_text(encoding="utf-8")),
                json.loads((EXPECTED / "happy-summary.json").read_text(encoding="utf-8")),
            )

    def test_no_change_plan_publishes_reference_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            output_csv = workspace / "cleaned.csv"
            summary = workspace / "summary.json"

            completed = self.run_cli(
                "clean",
                str(FIXTURES / "no-changes-input.csv"),
                str(FIXTURES / "plan-no-changes.json"),
                str(output_csv),
                str(summary),
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(output_csv.read_bytes(), (EXPECTED / "no-changes-cleaned.csv").read_bytes())
            self.assertEqual(
                json.loads(summary.read_text(encoding="utf-8")),
                json.loads((EXPECTED / "no-changes-summary.json").read_text(encoding="utf-8")),
            )

    def test_usage_errors_use_exit_code_two_without_outputs(self) -> None:
        completed = self.run_cli("invalid-command")

        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stdout, "")
        self.assertIn("Usage:", completed.stderr)

    def test_invalid_inputs_and_conflicting_outputs_fail_without_publication(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            output_csv = workspace / "cleaned.csv"
            summary = workspace / "summary.json"
            source_before = (FIXTURES / "happy-input.csv").read_bytes()

            invalid_plan = self.run_cli(
                "clean", str(FIXTURES / "happy-input.csv"), str(FIXTURES / "invalid-plan-version.json"), str(output_csv), str(summary)
            )
            self.assertEqual(invalid_plan.returncode, 1)
            self.assertEqual(invalid_plan.stdout, "")
            self.assertIn("plan_unsupported_version", invalid_plan.stderr)
            self.assertFalse(output_csv.exists())
            self.assertFalse(summary.exists())

            conflict = self.run_cli(
                "clean", str(FIXTURES / "happy-input.csv"), str(FIXTURES / "plan-all-operations.json"), str(FIXTURES / "happy-input.csv"), str(summary)
            )
            self.assertEqual(conflict.returncode, 1)
            self.assertEqual(conflict.stdout, "")
            self.assertIn("output_path_conflict", conflict.stderr)
            self.assertFalse(summary.exists())
            self.assertEqual((FIXTURES / "happy-input.csv").read_bytes(), source_before)

    def test_missing_source_fails_without_creating_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            completed = self.run_cli(
                "clean", str(workspace / "missing.csv"), str(FIXTURES / "plan-all-operations.json"), str(workspace / "cleaned.csv"), str(workspace / "summary.json")
            )

            self.assertEqual(completed.returncode, 1)
            self.assertEqual(completed.stdout, "")
            self.assertIn("source_path_invalid", completed.stderr)
            self.assertFalse((workspace / "cleaned.csv").exists())
            self.assertFalse((workspace / "summary.json").exists())

    def test_second_publication_failure_removes_owned_partial_result_and_temporaries(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            result = clean_dataset(
                load_csv(FIXTURES / "happy-input.csv"),
                load_plan(FIXTURES / "plan-all-operations.json"),
            )
            paths = ExecutionPaths(
                source=(FIXTURES / "happy-input.csv").resolve(),
                plan=(FIXTURES / "plan-all-operations.json").resolve(),
                output_csv=workspace / "cleaned.csv",
                summary_json=workspace / "summary.json",
            )
            original_replace = __import__("output").os.replace
            calls = 0

            def replace_then_fail(source: str | Path, destination: str | Path) -> None:
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("injected publication failure")
                original_replace(source, destination)

            with patch("output.os.replace", side_effect=replace_then_fail):
                with self.assertRaisesRegex(PublicationError, "publication_failed"):
                    publish_result(result, paths)

            self.assertFalse(paths.output_csv.exists())
            self.assertFalse(paths.summary_json.exists())
            self.assertEqual(list(workspace.glob(".csv-cleaner-*")), [])
