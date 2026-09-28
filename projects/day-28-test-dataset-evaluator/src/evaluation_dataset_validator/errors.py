"""Errores controlados y códigos de salida estables de la CLI."""

from __future__ import annotations

from enum import IntEnum
from pathlib import Path


class ExitCode(IntEnum):
    """Códigos de salida públicos de la interfaz de línea de comandos."""

    SUCCESS = 0
    VALIDATION_ERRORS = 1
    INVALID_INPUT = 2
    FILE_ERROR = 3
    CONFIG_ERROR = 4


class ApplicationError(Exception):
    """Base para fallos esperados con un código de salida y mensaje estable."""

    exit_code: ExitCode

    def __init__(self, message: str, exit_code: ExitCode) -> None:
        super().__init__(message)
        self.exit_code = exit_code


class FileAccessError(ApplicationError):
    """El archivo de entrada o configuración no se puede leer."""

    def __init__(self, source: Path) -> None:
        super().__init__(f"No se puede leer el archivo: {source}.", ExitCode.FILE_ERROR)


class InvalidJsonError(ApplicationError):
    """El contenido de un archivo no es JSON válido."""

    def __init__(self, source: Path, detail: str) -> None:
        super().__init__(f"JSON inválido en {source}: {detail}.", ExitCode.INVALID_INPUT)


class InvalidDatasetError(ApplicationError):
    """La raíz JSON del dataset no tiene la forma admitida."""

    def __init__(self, message: str) -> None:
        super().__init__(message, ExitCode.INVALID_INPUT)


class InvalidConfigurationError(ApplicationError):
    """La configuración existe pero incumple el contrato de opciones."""

    def __init__(self, source: Path, detail: str) -> None:
        super().__init__(f"Configuración inválida en {source}: {detail}.", ExitCode.CONFIG_ERROR)
