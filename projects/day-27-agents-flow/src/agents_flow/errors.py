"""Errores de dominio con códigos estables para la interfaz de línea de comandos."""

from __future__ import annotations


class DomainError(Exception):
    """Error controlado que puede exponerse mediante el contrato de la CLI."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class ValidationError(DomainError):
    """Error de validación de una entrada o contrato público."""


class StageError(DomainError):
    """Controlled failure raised when a named workflow stage cannot complete."""

    def __init__(self, stage: str, cause: DomainError | Exception) -> None:
        self.stage = stage
        self.cause = cause
        message = f"{stage} stage failed: {cause}"
        super().__init__(f"{stage}_stage_failed", message)
