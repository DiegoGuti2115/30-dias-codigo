"""Comprobación local reproducible para pre-commit y CI sin dependencias extra."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    """Run the project's portable quality gate using the active Python interpreter."""
    commands = (
        (sys.executable, "-m", "compileall", "-q", "src", "tests"),
        (sys.executable, "-m", "pytest"),
    )
    for command in commands:
        result = subprocess.run(command, cwd=PROJECT_ROOT, check=False)
        if result.returncode:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
