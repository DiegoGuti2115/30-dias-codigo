"""Comprobación local de patrones de secretos en archivos versionables.

No sustituye un gestor de secretos ni una revisión humana. Evita incluir archivos de
entorno, dependencias o artefactos generados para mantener la comprobación local y
reproducible.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INCLUDED_DIRECTORIES = ("backend", "frontend/src", "frontend/tests", "shared", "data", "docs", "scripts")
INCLUDED_FILES = ("README.md", "ROADMAP.md", ".env.example")
SKIPPED_PARTS = {"node_modules", ".next", ".venv", "__pycache__", ".pytest_cache"}
ALLOWED_SUFFIXES = {".py", ".ts", ".tsx", ".json", ".md", ".cmd", ".css", ".mjs", ".yml", ".yaml", ".example"}
PATTERNS = (
    ("clave privada", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("clave AWS", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("token de proveedor", re.compile(r"\b(?:ghp|github_pat|sk|rk)_[A-Za-z0-9_-]{20,}\b")),
    ("asignación de secreto", re.compile(r"(?i)\b(?:api[_-]?key|secret|token|password)\b\s*[:=]\s*[\"'][^\"']{8,}[\"']")),
)


def candidate_files() -> list[Path]:
    files = [ROOT / file_name for file_name in INCLUDED_FILES if (ROOT / file_name).is_file()]
    for relative_directory in INCLUDED_DIRECTORIES:
        directory = ROOT / relative_directory
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if path.is_file() and not (set(path.parts) & SKIPPED_PARTS) and path.suffix in ALLOWED_SUFFIXES:
                files.append(path)
    return files


def main() -> int:
    findings: list[str] = []
    for path in candidate_files():
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(content.splitlines(), start=1):
            for label, pattern in PATTERNS:
                if pattern.search(line):
                    findings.append(f"{path.relative_to(ROOT)}:{line_number}: posible {label}")

    if findings:
        print("La comprobación local detectó posibles secretos:")
        print("\n".join(findings))
        return 1

    print("No se detectaron patrones de secretos en los archivos de proyecto revisados.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
