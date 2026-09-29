"""Configuración y preocupaciones transversales de la aplicación."""

from .authentication import IdentityProvider
from .settings import Settings, get_settings

__all__ = ["IdentityProvider", "Settings", "get_settings"]
