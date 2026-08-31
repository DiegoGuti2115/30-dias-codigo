"""Integration tests for the standard-library JSON and CSV web interface."""

from __future__ import annotations

import base64
import json
import sys
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

PROJECT_DIRECTORY = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = PROJECT_DIRECTORY / "src"
sys.path.insert(0, str(SOURCE_DIRECTORY))

from validators import ConversionError  # noqa: E402
from web import ConverterWebHandler, convert_request  # noqa: E402


class WebConversionTests(unittest.TestCase):
    """Verify the web adapter delegates validation and output creation to the core."""

    def test_json_to_csv_returns_preview_count_and_download(self) -> None:
        response = convert_request(
            {
                "direction": "json-to-csv",
                "filename": "people.json",
                "content": '[{"name":"Ada","active":true},{"name":"Lin","note":"hello, world"}]',
            }
        )

        self.assertEqual(response["count"], 2)
        self.assertEqual(response["output_name"], "people.csv")
        self.assertIn("name,active,note", response["preview"])
        self.assertIn('Lin,,"hello, world"', response["preview"])
        self.assertTrue(response["download_url"].startswith("data:text/csv;base64,"))
        encoded_file = response["download_url"].split(",", maxsplit=1)[1]
        self.assertEqual(base64.b64decode(encoded_file).decode("utf-8"), response["preview"])

    def test_csv_to_json_preserves_text_and_exposes_download(self) -> None:
        response = convert_request(
            {
                "direction": "csv-to-json",
                "filename": "catalog.csv",
                "content": "code,available\n0012,true\n",
            }
        )

        self.assertEqual(response["count"], 1)
        self.assertEqual(response["output_name"], "catalog.json")
        self.assertEqual(json.loads(response["preview"]), [{"code": "0012", "available": "true"}])
        self.assertTrue(response["download_url"].startswith("data:application/json;base64,"))

    def test_invalid_request_is_rejected_with_core_validation_errors(self) -> None:
        with self.assertRaisesRegex(ConversionError, "no puede estar vacío"):
            convert_request(
                {
                    "direction": "json-to-csv",
                    "filename": "empty.json",
                    "content": "[]",
                }
            )
        with self.assertRaisesRegex(ConversionError, "extensión .csv"):
            convert_request(
                {
                    "direction": "csv-to-json",
                    "filename": "wrong.json",
                    "content": "key\nvalue\n",
                }
            )

    def test_handler_page_includes_accessible_workflow_controls(self) -> None:
        page = __import__("web").PAGE
        self.assertIn('aria-live="polite"', page)
        self.assertIn("Vista previa del resultado", page)
        self.assertIn("Reglas reales de esta versión", page)
        self.assertIn("/api/convert", page)

    def test_http_api_serves_page_converts_and_returns_validation_error(self) -> None:
        server = ThreadingHTTPServer(("127.0.0.1", 0), ConverterWebHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base_url = f"http://127.0.0.1:{server.server_port}"
        try:
            with urlopen(f"{base_url}/", timeout=3) as response:
                page = response.read().decode("utf-8")
            self.assertIn("Convertidor JSON", page)

            request = Request(
                f"{base_url}/api/convert",
                data=json.dumps(
                    {
                        "direction": "csv-to-json",
                        "filename": "sample.csv",
                        "content": "id\n0012\n",
                    }
                ).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(request, timeout=3) as response:
                payload = json.loads(response.read().decode("utf-8"))
            self.assertEqual(payload["count"], 1)
            self.assertEqual(json.loads(payload["preview"]), [{"id": "0012"}])

            invalid = Request(
                f"{base_url}/api/convert",
                data=b'{"direction":"json-to-csv","filename":"empty.json","content":"[]"}',
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with self.assertRaises(HTTPError) as error:
                urlopen(invalid, timeout=3)
            self.assertEqual(error.exception.code, 400)
            self.assertIn("no puede estar vacío", error.exception.read().decode("utf-8"))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


if __name__ == "__main__":
    unittest.main()
