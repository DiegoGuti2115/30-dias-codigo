"""Pure evaluation of the fixed password policy v1.

No function in this module performs input/output, persistence, logging, or
formatting.  Evaluation results carry rule states only and never retain the input.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final
from unicodedata import category

from policy import POLICY_V1, PasswordPolicy


INVALID_PASSWORD_TYPE_MESSAGE: Final = "La entrada para evaluación debe ser texto Unicode."


@dataclass(frozen=True, slots=True)
class RuleResult:
    """The outcome of one principal policy rule."""

    identifier: str
    is_satisfied: bool


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """A complete, secret-free evaluation outcome in contractual rule order."""

    is_valid: bool
    rules: tuple[RuleResult, ...]
    has_whitespace: bool


def validate_password(
    password: str, policy: PasswordPolicy = POLICY_V1
) -> ValidationResult:
    """Evaluate *password* fully against the supplied fixed-policy representation.

    The input must be a Unicode text string.  Every main rule is evaluated even
    when an earlier rule fails; whitespace is evaluated separately after them.
    """
    if not isinstance(password, str):
        raise TypeError(INVALID_PASSWORD_TYPE_MESSAGE)

    has_whitespace = any(character.isspace() for character in password)
    outcomes = {
        "length": policy.minimum_length <= len(password) <= policy.maximum_length,
        "uppercase": any(character.isupper() for character in password),
        "lowercase": any(character.islower() for character in password),
        "digit": any(character.isdecimal() for character in password),
        "special": any(
            not character.isspace()
            and not character.isalpha()
            and not character.isdecimal()
            and not category(character).startswith("M")
            for character in password
        ),
    }
    rules = tuple(
        RuleResult(identifier=rule.identifier, is_satisfied=outcomes[rule.identifier])
        for rule in policy.rules
    )

    return ValidationResult(
        is_valid=all(rule.is_satisfied for rule in rules) and not has_whitespace,
        rules=rules,
        has_whitespace=has_whitespace,
    )
