"""End-to-end local coverage for the Phase 4 command-line interface."""

from __future__ import annotations

import json
import os
import subprocess
from unittest.mock import patch
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
CLI_PATH = SRC_ROOT / "main.py"


class BackupCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temporary_directory.name)
        self.destination = self.workspace / "backups"
        self.destination.mkdir()
        self.fixtures = PROJECT_ROOT / "data" / "fixtures"
        self.expected = json.loads(
            (PROJECT_ROOT / "data" / "expected" / "local-copy-manifests.json").read_text(
                encoding="utf-8"
            )
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _run_cli(
        self,
        *arguments: str,
        cwd: Path | None = None,
        environment: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CLI_PATH), *arguments],
            cwd=cwd or PROJECT_ROOT,
            env=environment if environment is not None else os.environ.copy(),
            text=True,
            capture_output=True,
            check=False,
        )

    def test_backup_file_succeeds_with_a_stable_local_confirmation(self) -> None:
        source = self.fixtures / "regular-file" / "sample-note.txt"

        result = self._run_cli("backup", str(source), str(self.destination))

        final_path = self.destination / source.name
        self.assertEqual(0, result.returncode)
        self.assertEqual(f"Local backup verified: {final_path}\n", result.stdout)
        self.assertEqual("", result.stderr)
        self.assertEqual(source.read_bytes(), final_path.read_bytes())
        self.assertEqual(
            self.expected["manifests"]["regular-file-success"]["files"][0]["size_bytes"],
            final_path.stat().st_size,
        )

    def test_relative_paths_work_from_the_execution_directory(self) -> None:
        source = self.workspace / "source.txt"
        source.write_text("relative fixture", encoding="utf-8")
        destination = self.workspace / "backups"
        relative_result = self._run_cli("backup", "source.txt", "backups", cwd=self.workspace)

        self.assertEqual(0, relative_result.returncode)
        self.assertEqual(f"Local backup verified: {destination / source.name}\n", relative_result.stdout)
        self.assertEqual("relative fixture", (destination / source.name).read_text(encoding="utf-8"))

    def test_directory_and_empty_directory_flow_preserve_reference_properties(self) -> None:
        source = self.fixtures / "directory-tree"

        directory_result = self._run_cli("backup", str(source), str(self.destination))

        copied_tree = self.destination / source.name
        self.assertEqual(0, directory_result.returncode)
        self.assertTrue((copied_tree / "empty-folder").is_dir())
        self.assertEqual("", directory_result.stderr)

        empty_source = self.workspace / "empty-source"
        empty_source.mkdir()
        empty_result = self._run_cli("backup", str(empty_source), str(self.destination))
        self.assertEqual(0, empty_result.returncode)
        self.assertEqual([], list((self.destination / empty_source.name).iterdir()))

    def test_invalid_syntax_returns_usage_exit_code_without_creating_content(self) -> None:
        result = self._run_cli("backup")

        self.assertEqual(2, result.returncode)
        self.assertEqual("", result.stdout)
        self.assertIn("usage:", result.stderr.lower())
        self.assertFalse(any(self.destination.iterdir()))

    def test_unknown_command_and_option_return_usage_exit_code(self) -> None:
        unknown_command = self._run_cli("restore")
        unknown_option = self._run_cli(
            "backup",
            str(self.fixtures / "regular-file" / "sample-note.txt"),
            str(self.destination),
            "--unknown",
        )

        self.assertEqual(2, unknown_command.returncode)
        self.assertEqual(2, unknown_option.returncode)
        self.assertEqual("", unknown_command.stdout)
        self.assertEqual("", unknown_option.stdout)
        self.assertIn("usage:", unknown_command.stderr.lower())
        self.assertIn("usage:", unknown_option.stderr.lower())
        self.assertFalse(any(self.destination.iterdir()))

    def test_local_validation_failure_is_concise_and_does_not_publish(self) -> None:
        missing_source = self.workspace / "missing.txt"

        result = self._run_cli("backup", str(missing_source), str(self.destination))

        self.assertEqual(1, result.returncode)
        self.assertEqual("", result.stdout)
        self.assertIn("Local backup failed:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertFalse(any(self.destination.iterdir()))

    def test_existing_final_entry_remains_unchanged_and_second_run_fails(self) -> None:
        source = self.fixtures / "regular-file" / "sample-note.txt"
        first = self._run_cli("backup", str(source), str(self.destination))
        copied = self.destination / source.name
        before = copied.read_bytes()
        second = self._run_cli("backup", str(source), str(self.destination))

        self.assertEqual(0, first.returncode)
        self.assertEqual(1, second.returncode)
        self.assertEqual(before, copied.read_bytes())
        self.assertEqual([], list(self.destination.glob(".backup-v1-*.tmp")))

    def test_azure_request_without_configuration_fails_before_local_mutation(self) -> None:
        source = self.fixtures / "regular-file" / "sample-note.txt"
        environment = os.environ.copy()
        environment.pop("AZURE_STORAGE_CONNECTION_STRING", None)
        environment.pop("AZURE_STORAGE_CONTAINER_NAME", None)

        result = self._run_cli("backup", str(source), str(self.destination), "--azure", environment=environment)

        self.assertEqual(1, result.returncode)
        self.assertEqual("", result.stdout)
        self.assertIn("Azure backup failed:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertFalse(any(self.destination.iterdir()))

    def test_azure_success_and_post_publication_failure_keep_the_local_result(self) -> None:
        sys.path.insert(0, str(SRC_ROOT))
        from contextlib import redirect_stderr, redirect_stdout
        from io import StringIO

        from main import run_cli  # noqa: PLC0415
        from models import BackupResult, RemoteBackupResult  # noqa: PLC0415

        final_path = self.destination / "published.txt"

        def successful_local(_source: str, _destination: str) -> BackupResult:
            return BackupResult(True, final_path=final_path)

        stdout = StringIO()
        stderr = StringIO()
        with patch.dict(os.environ, {
            "AZURE_STORAGE_CONNECTION_STRING": "test-connection-string",
            "AZURE_STORAGE_CONTAINER_NAME": "test-container",
        }, clear=False), redirect_stdout(stdout), redirect_stderr(stderr):
            code = run_cli(
                ["backup", "source", "destination", "--azure"],
                backup_runner=successful_local,
                remote_runner=lambda _path: RemoteBackupResult(True, uploaded_blobs=2),
            )
        self.assertEqual(0, code)
        self.assertEqual(
            f"Local backup verified: {final_path}\nAzure backup verified: 2 blob(s) uploaded.\n",
            stdout.getvalue(),
        )
        self.assertEqual("", stderr.getvalue())

        stdout = StringIO()
        stderr = StringIO()
        with patch.dict(os.environ, {
            "AZURE_STORAGE_CONNECTION_STRING": "test-connection-string",
            "AZURE_STORAGE_CONTAINER_NAME": "test-container",
        }, clear=False), redirect_stdout(stdout), redirect_stderr(stderr):
            code = run_cli(
                ["backup", "source", "destination", "--azure"],
                backup_runner=successful_local,
                remote_runner=lambda _path: RemoteBackupResult(False, message="Azure backup failed; local fallback retained."),
            )
        self.assertEqual(0, code)
        self.assertEqual(f"Local backup verified: {final_path}\n", stdout.getvalue())
        self.assertEqual("Azure backup failed; local fallback retained.\n", stderr.getvalue())

    def test_interrupted_process_is_reported_without_a_traceback(self) -> None:
        sys.path.insert(0, str(SRC_ROOT))
        from main import run_cli  # noqa: PLC0415

        def interrupted_runner(_source: str, _destination: str):
            raise KeyboardInterrupt

        # The direct boundary lets the CLI be tested without spawning a signal-capable process.
        from contextlib import redirect_stderr, redirect_stdout
        from io import StringIO

        stdout = StringIO()
        stderr = StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = run_cli(["backup", "source", "destination"], backup_runner=interrupted_runner)
        self.assertEqual(1, code)
        self.assertEqual("", stdout.getvalue())
        self.assertEqual("Local backup interrupted before completion.\n", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
