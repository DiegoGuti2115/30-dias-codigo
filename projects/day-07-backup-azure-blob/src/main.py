"""Command-line interface for the verified local backup workflow."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

from azure_blob import azure_configuration_error, upload_local_backup
from local_backup import run_local_backup
from models import BackupResult, RemoteBackupResult

BackupRunner = Callable[[str | Path, str | Path], BackupResult]
RemoteRunner = Callable[[Path], RemoteBackupResult]


class BackupArgumentParser(argparse.ArgumentParser):
    """Keep invalid invocations on stderr with the contract's exit code 2."""

    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        self.exit(2, f"backup: error: {message}\n")


def create_parser() -> argparse.ArgumentParser:
    """Create the single-command v1 interface defined by the contract."""
    parser = BackupArgumentParser(
        prog="python src/main.py",
        description="Create one verified local backup without modifying its source.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")
    backup = subcommands.add_parser(
        "backup",
        help="copy one regular file or directory into an existing destination directory",
    )
    backup.add_argument("source_path", metavar="SOURCE_PATH")
    backup.add_argument("destination_directory", metavar="DESTINATION_DIRECTORY")
    backup.add_argument(
        "--azure",
        action="store_true",
        help="request the optional Azure destination after the local backup",
    )
    return parser


def _report_local_failure(result: BackupResult) -> int:
    message = result.message or "local backup could not be completed"
    print(f"Local backup failed: {message}", file=sys.stderr)
    if result.cleanup_warning:
        print("Cleanup warning: owned temporary backup data could not be removed.", file=sys.stderr)
    return 1


def _report_azure_failure(message: str) -> int:
    print(f"Azure backup failed: {message}", file=sys.stderr)
    return 1


def run_cli(
    arguments: Sequence[str] | None = None,
    *,
    backup_runner: BackupRunner = run_local_backup,
    remote_runner: RemoteRunner = upload_local_backup,
) -> int:
    """Execute the contracted CLI and return its process exit code."""
    parser = create_parser()
    namespace = parser.parse_args(arguments)

    if namespace.azure:
        configuration_error = azure_configuration_error()
        if configuration_error:
            return _report_azure_failure(configuration_error)

    try:
        result = backup_runner(namespace.source_path, namespace.destination_directory)
    except KeyboardInterrupt:
        print("Local backup interrupted before completion.", file=sys.stderr)
        return 1
    except Exception:
        print("Local backup failed due to an unexpected local error.", file=sys.stderr)
        return 1

    if not result.success:
        return _report_local_failure(result)

    print(f"Local backup verified: {result.final_path}")
    if not namespace.azure:
        return 0

    try:
        remote_result = remote_runner(result.final_path)
    except KeyboardInterrupt:
        print("Azure backup interrupted; local fallback retained.", file=sys.stderr)
        return 0
    except Exception:
        print("Azure backup failed; local fallback retained.", file=sys.stderr)
        return 0

    if remote_result.success:
        print(f"Azure backup verified: {remote_result.uploaded_blobs} blob(s) uploaded.")
    else:
        print(remote_result.message or "Azure backup failed; local fallback retained.", file=sys.stderr)
    return 0


def main() -> None:
    """Process entry point used by ``python src/main.py``."""
    raise SystemExit(run_cli())


if __name__ == "__main__":
    main()
