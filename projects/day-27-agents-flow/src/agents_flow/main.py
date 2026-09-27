"""Command-line presentation of the deterministic local workflow."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from typing import TextIO

from .contracts import Request, WorkflowResult
from .errors import DomainError, ValidationError
from .orchestrator import WorkflowOrchestrator
from .presentation import serialize_workflow

VALIDATION_EXIT_CODE = 2


def build_parser() -> argparse.ArgumentParser:
    """Create the parser without starting agents or external providers."""

    parser = argparse.ArgumentParser(
        prog="agents-flow",
        description=(
            "Ejecuta el flujo local determinista de investigación, redacción y revisión. "
            "La salida se emite como JSON UTF-8."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Solicitud textual no vacía para el flujo de agentes.",
    )
    parser.add_argument(
        "--format",
        choices=("json",),
        default="json",
        help="Formato de salida admitido (predeterminado: json).",
    )
    return parser


def serialize_contract(result: WorkflowResult, output_format: str) -> dict[str, object]:
    """Convierte el resultado temporal de Fase 1 en la respuesta pública JSON."""

    if output_format != "json":
        raise ValidationError("invalid_format", "format must be 'json'")
    return {
        "format": output_format,
        "phase": result.phase,
        "request": {"prompt": result.request.prompt},
        "status": result.status,
    }


def write_domain_error(error: DomainError, stream: TextIO) -> None:
    """Emite un error estable en stderr sin mezclarlo con la salida correcta."""

    print(
        json.dumps(
            {"error": {"code": error.code, "message": error.message}},
            ensure_ascii=False,
        ),
        file=stream,
    )


def main(
    argv: Sequence[str] | None = None,
    *,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
    orchestrator: WorkflowOrchestrator | None = None,
) -> int:
    """Run the complete local workflow and write its public JSON representation."""

    import sys

    output = stdout or sys.stdout
    errors = stderr or sys.stderr
    parser = build_parser()
    arguments = parser.parse_args(argv)

    try:
        request = Request(arguments.prompt)
        result = (orchestrator or WorkflowOrchestrator()).run(request)
        print(
            json.dumps(serialize_workflow(result, arguments.format), ensure_ascii=False),
            file=output,
        )
    except DomainError as error:
        write_domain_error(error, errors)
        return VALIDATION_EXIT_CODE

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
