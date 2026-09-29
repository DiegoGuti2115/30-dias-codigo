"""Puerto de identidad reservado para una fase posterior.

No implementa cuentas, sesiones, tokens ni autorización.
"""

from typing import Protocol


class IdentityProvider(Protocol):
    """Resuelve una identidad autenticada cuando exista un proveedor aprobado."""

    def get_subject_id(self) -> str:
        """Devuelve un identificador opaco de sujeto autenticado."""
