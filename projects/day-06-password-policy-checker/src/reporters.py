"""Safe, deterministic presentation for password-policy evaluation results.

The formatter accepts a secret-free ValidationResult and returns only the global
status plus contractual failure messages. It never receives the evaluated input.
"""

from __future__ import annotations

from typing import Final

from policy import POLICY_V1, PasswordPolicy
from validator import ValidationResult


VALID_MESSAGE: Final = "Contraseña válida según la política v1."
INVALID_MESSAGE: Final = "Contraseña no válida según la política v1."


def format_validation_result(
    result: ValidationResult, policy: PasswordPolicy = POLICY_V1
) -> str:
    """Return deterministic, contract-approved output without sensitive details."""
    lines = [VALID_MESSAGE if result.is_valid else INVALID_MESSAGE]
    messages = {rule.identifier: rule.failure_message for rule in policy.rules}

    for rule in result.rules:
        if not rule.is_satisfied:
            lines.append(messages[rule.identifier])
    if result.has_whitespace:
        lines.append(policy.whitespace_failure_message)

    return "\n".join(lines) + "\n"
