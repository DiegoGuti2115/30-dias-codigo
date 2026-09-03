"""Immutable representation of the fixed password policy v1.

This module is intentionally pure: it neither receives interactive input nor emits
output.  The constants and rule order mirror docs/CONTRATO.md exactly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True, slots=True)
class Rule:
    """One required rule in the fixed policy, with a stable public identifier."""

    identifier: str
    failure_message: str


@dataclass(frozen=True, slots=True)
class PasswordPolicy:
    """The immutable thresholds and ordered rules for policy version 1."""

    minimum_length: int
    maximum_length: int
    rules: tuple[Rule, ...]
    whitespace_failure_message: str


RULES: Final[tuple[Rule, ...]] = (
    Rule("length", "No cumple la longitud requerida."),
    Rule("uppercase", "Falta una letra mayúscula."),
    Rule("lowercase", "Falta una letra minúscula."),
    Rule("digit", "Falta un dígito decimal."),
    Rule("special", "Falta un carácter especial."),
)

POLICY_V1: Final = PasswordPolicy(
    minimum_length=12,
    maximum_length=128,
    rules=RULES,
    whitespace_failure_message="No se permiten espacios en blanco.",
)
