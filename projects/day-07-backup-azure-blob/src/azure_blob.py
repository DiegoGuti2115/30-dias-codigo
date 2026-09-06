"""Optional Azure Blob adapter with deferred SDK loading and controlled results."""

from __future__ import annotations

import os
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Protocol

from models import RemoteBackupResult
from verification import build_manifest

_CONNECTION_STRING = "AZURE_STORAGE_CONNECTION_STRING"
_CONTAINER_NAME = "AZURE_STORAGE_CONTAINER_NAME"
_BLOB_PREFIX = "backups"


class BlobClient(Protocol):
    """Subset of the Azure blob client used by this adapter."""

    def upload_blob(self, data: object, *, overwrite: bool) -> object: ...


class ContainerClient(Protocol):
    """Subset of the Azure container client used by this adapter."""

    def get_blob_client(self, blob: str) -> BlobClient: ...


class BlobServiceClient(Protocol):
    """Subset of the Azure service client used by this adapter."""

    def get_container_client(self, container: str) -> ContainerClient: ...


ServiceClientFactory = Callable[[str], BlobServiceClient]


def azure_configuration_error(environment: Mapping[str, str] | None = None) -> str | None:
    """Return a safe missing-configuration error without exposing environment values."""
    values = os.environ if environment is None else environment
    missing = [name for name in (_CONNECTION_STRING, _CONTAINER_NAME) if not values.get(name, "").strip()]
    if missing:
        return "Azure backup requires connection string and container configuration."
    return None


def _default_service_client_factory(connection_string: str) -> BlobServiceClient:
    """Import the optional SDK only after Azure was explicitly requested."""
    try:
        from azure.storage.blob import BlobServiceClient as AzureBlobServiceClient
    except ImportError as error:
        raise RuntimeError("Azure Blob SDK is not installed") from error
    return AzureBlobServiceClient.from_connection_string(connection_string)


def _blob_name(root: Path, relative_path: str) -> str:
    if relative_path == ".":
        return f"{_BLOB_PREFIX}/{root.name}"
    return f"{_BLOB_PREFIX}/{root.name}/{relative_path}"


def upload_local_backup(
    root: Path,
    *,
    environment: Mapping[str, str] | None = None,
    service_client_factory: ServiceClientFactory = _default_service_client_factory,
) -> RemoteBackupResult:
    """Upload published regular files, never overwrite blobs, and suppress provider details."""
    values = os.environ if environment is None else environment
    configuration_error = azure_configuration_error(values)
    if configuration_error:
        return RemoteBackupResult(False, message=configuration_error)

    try:
        manifest = build_manifest(root)
        service_client = service_client_factory(values[_CONNECTION_STRING])
        container_client = service_client.get_container_client(values[_CONTAINER_NAME])
        for entry in manifest.files:
            relative_path = entry.relative_path
            local_path = root if relative_path == "." else root / Path(relative_path)
            with local_path.open("rb") as source:
                container_client.get_blob_client(_blob_name(root, relative_path)).upload_blob(
                    source, overwrite=False
                )
    except KeyboardInterrupt:
        raise
    except Exception:
        return RemoteBackupResult(False, message="Azure backup failed; local fallback retained.")

    return RemoteBackupResult(True, uploaded_blobs=len(manifest.files))
