"""Domain errors exposed by the local CLI without internal tracebacks."""

from __future__ import annotations


class ValidationError(Exception):
    """Raised when a Phase 2 request or corpus violates the public contract."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
