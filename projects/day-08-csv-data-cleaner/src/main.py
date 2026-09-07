"""Command-line entry point for the contractual Day 08 CSV cleaner."""

from __future__ import annotations

import sys
from collections.abc import Sequence
from pathlib import Path

from cleaner import clean_dataset
from csv_profile import CsvContractError, load_csv
from output import PathValidationError, PublicationError, publish_result, validate_execution_paths
from plan import PlanValidationError, load_plan

USAGE = "Usage: python src/main.py clean <SOURCE_CSV> <PLAN_JSON> <OUTPUT_CSV> <SUMMARY_JSON>"


def main(arguments: Sequence[str] | None = None) -> int:
    """Run the sole v1 command and return only contractual exit codes."""

    args = list(sys.argv[1:] if arguments is None else arguments)
    if len(args) != 5 or args[0] != "clean":
        print(USAGE, file=sys.stderr)
        return 2

    _, source, plan, output_csv, summary_json = args
    try:
        paths = validate_execution_paths(source, plan, output_csv, summary_json)
        cleaning_plan = load_plan(paths.plan)
        dataset = load_csv(paths.source)
        result = clean_dataset(dataset, cleaning_plan)
        publish_result(result, paths)
    except (PathValidationError, PlanValidationError, CsvContractError, PublicationError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Error: operation_interrupted", file=sys.stderr)
        return 1

    print(f"Created cleaned CSV: {_display_path(paths.output_csv)}")
    print(f"Created summary JSON: {_display_path(paths.summary_json)}")
    return 0


def _display_path(path: Path) -> Path:
    """Avoid exposing the current user's absolute workspace path when possible."""

    try:
        return path.relative_to(Path.cwd().resolve())
    except ValueError:
        return path


if __name__ == "__main__":
    raise SystemExit(main())
