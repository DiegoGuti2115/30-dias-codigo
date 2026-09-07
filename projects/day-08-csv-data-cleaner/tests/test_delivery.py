from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
FIXTURES = PROJECT_ROOT / "data" / "fixtures"
EXPECTED = PROJECT_ROOT / "data" / "expected"


class DeliveryQualityTests(unittest.TestCase):
    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SRC / "main.py"), *arguments],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

    def test_repeated_runs_are_byte_deterministic_and_preserve_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            source = workspace / "happy-input.csv"
            plan = workspace / "plan.json"
            source.write_bytes((FIXTURES / "happy-input.csv").read_bytes())
            plan.write_bytes((FIXTURES / "plan-all-operations.json").read_bytes())
            source_before = source.read_bytes()

            output_pairs = []
            for run_number in (1, 2):
                output_csv = workspace / f"cleaned-{run_number}.csv"
                summary = workspace / f"summary-{run_number}.json"
                completed = self.run_cli("clean", str(source), str(plan), str(output_csv), str(summary))
                self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertEqual(completed.stderr, "")
                output_pairs.append((output_csv.read_bytes(), summary.read_bytes()))

            self.assertEqual(output_pairs[0], output_pairs[1])
            self.assertEqual(output_pairs[0][0], (EXPECTED / "happy-cleaned.csv").read_bytes())
            self.assertEqual(
                json.loads(output_pairs[0][1].decode("utf-8")),
                json.loads((EXPECTED / "happy-summary.json").read_text(encoding="utf-8")),
            )
            self.assertEqual(source.read_bytes(), source_before)

    def test_contractual_limits_fail_without_outputs_or_cell_data_in_errors(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            oversized_source = workspace / "oversized.csv"
            oversized_source.write_bytes(b"column\n" + (b"x" * (10 * 1024 * 1024)))
            output_csv = workspace / "cleaned.csv"
            summary = workspace / "summary.json"

            completed = self.run_cli(
                "clean",
                str(oversized_source),
                str(FIXTURES / "plan-no-changes.json"),
                str(output_csv),
                str(summary),
            )

            self.assertEqual(completed.returncode, 1)
            self.assertEqual(completed.stdout, "")
            self.assertIn("csv_size_limit", completed.stderr)
            self.assertNotIn("x" * 100, completed.stderr)
            self.assertFalse(output_csv.exists())
            self.assertFalse(summary.exists())

    def test_delivery_documentation_and_project_artifacts_are_safe(self) -> None:
        required_files = (
            PROJECT_ROOT / "README.md",
            PROJECT_ROOT / "ROADMAP.md",
            PROJECT_ROOT / "docs" / "CONTRATO.md",
            PROJECT_ROOT / "docs" / "VERIFICACION_FASE_5.md",
            PROJECT_ROOT / "docs" / "LINKEDIN_DIA_08.md",
            PROJECT_ROOT / "examples" / "USO.md",
            PROJECT_ROOT / "assets" / "DEMO_15S.md",
        )
        for path in required_files:
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())

        self.assertFalse(list(PROJECT_ROOT.rglob(".csv-cleaner-*")))
        self.assertFalse(list(PROJECT_ROOT.rglob("demo-tmp")))
        self.assertFalse(list(PROJECT_ROOT.rglob("tmp")))
        self.assertFalse(list(PROJECT_ROOT.rglob(".env")))
        self.assertFalse(list(PROJECT_ROOT.rglob("requirements*.txt")))
        self.assertFalse(list(PROJECT_ROOT.rglob("pyproject.toml")))
        self.assertFalse(list(PROJECT_ROOT.rglob("package.json")))


if __name__ == "__main__":
    unittest.main()
