"""Isolated coverage for the optional Azure Blob adapter; no SDK or network is used."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_ROOT))

from azure_blob import azure_configuration_error, upload_local_backup  # noqa: E402


class FakeBlobClient:
    def __init__(self, name: str, uploads: dict[str, bytes]) -> None:
        self.name = name
        self.uploads = uploads

    def upload_blob(self, data: object, *, overwrite: bool) -> object:
        self.uploads[self.name] = data.read()  # type: ignore[union-attr]
        self.uploads[f"{self.name}:overwrite"] = str(overwrite).encode()
        return object()


class FakeContainerClient:
    def __init__(self, uploads: dict[str, bytes]) -> None:
        self.uploads = uploads

    def get_blob_client(self, blob: str) -> FakeBlobClient:
        return FakeBlobClient(blob, self.uploads)


class FakeServiceClient:
    def __init__(self, uploads: dict[str, bytes]) -> None:
        self.uploads = uploads
        self.container_name: str | None = None

    def get_container_client(self, container: str) -> FakeContainerClient:
        self.container_name = container
        return FakeContainerClient(self.uploads)


class AzureBlobAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temporary_directory.name)
        self.environment = {
            "AZURE_STORAGE_CONNECTION_STRING": "test-connection-string",
            "AZURE_STORAGE_CONTAINER_NAME": "backup-container",
        }

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_missing_configuration_is_reported_without_exposing_variable_values(self) -> None:
        self.assertIsNotNone(azure_configuration_error({}))
        self.assertIsNotNone(azure_configuration_error({"AZURE_STORAGE_CONNECTION_STRING": "value"}))
        self.assertIsNone(azure_configuration_error(self.environment))

    def test_file_upload_uses_documented_prefix_and_never_overwrites(self) -> None:
        root = self.workspace / "note.txt"
        root.write_text("safe content", encoding="utf-8")
        uploads: dict[str, bytes] = {}
        service = FakeServiceClient(uploads)

        result = upload_local_backup(
            root,
            environment=self.environment,
            service_client_factory=lambda _connection: service,
        )

        self.assertTrue(result.success)
        self.assertEqual(1, result.uploaded_blobs)
        self.assertEqual("backup-container", service.container_name)
        self.assertEqual(b"safe content", uploads["backups/note.txt"])
        self.assertEqual(b"False", uploads["backups/note.txt:overwrite"])

    def test_directory_upload_uses_posix_relative_names_and_omits_empty_directories(self) -> None:
        root = self.workspace / "tree"
        (root / "nested").mkdir(parents=True)
        (root / "empty").mkdir()
        (root / "nested" / "entry.txt").write_text("nested", encoding="utf-8")
        uploads: dict[str, bytes] = {}

        result = upload_local_backup(
            root,
            environment=self.environment,
            service_client_factory=lambda _connection: FakeServiceClient(uploads),
        )

        self.assertTrue(result.success)
        self.assertEqual(1, result.uploaded_blobs)
        self.assertEqual(b"nested", uploads["backups/tree/nested/entry.txt"])
        self.assertFalse(any("empty" in name for name in uploads))

    def test_provider_failure_is_controlled_without_provider_detail(self) -> None:
        root = self.workspace / "note.txt"
        root.write_text("safe", encoding="utf-8")

        def unavailable(_connection: str) -> FakeServiceClient:
            raise RuntimeError("provider secret detail")

        result = upload_local_backup(root, environment=self.environment, service_client_factory=unavailable)

        self.assertFalse(result.success)
        self.assertEqual("Azure backup failed; local fallback retained.", result.message)
        self.assertNotIn("provider secret detail", result.message or "")


if __name__ == "__main__":
    unittest.main()
