"""Static safeguards for the local, educational web demonstration."""

from __future__ import annotations

import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEMO_PAGE = PROJECT_ROOT / "assets" / "demo-interactiva.html"
WEB_GUIDE = PROJECT_ROOT / "docs" / "WEB.md"


class WebDemoTests(unittest.TestCase):
    """Verify that the static landing preserves the documented local-only scope."""

    def test_demo_declares_its_educational_local_scope_and_contractual_messages(self) -> None:
        content = DEMO_PAGE.read_text(encoding="utf-8")

        for expected_text in (
            "Entorno educativo local:",
            "no realiza llamadas de red",
            "Contraseña válida según la política v1.",
            "Contraseña no válida según la política v1.",
            "No cumple la longitud requerida.",
            "No se permiten espacios en blanco.",
            "prefers-reduced-motion",
            "aria-live",
        ):
            with self.subTest(expected_text=expected_text):
                self.assertIn(expected_text, content)

    def test_demo_uses_no_remote_or_browser_persistence_api(self) -> None:
        content = DEMO_PAGE.read_text(encoding="utf-8").casefold()

        for prohibited_api in ("fetch(", "xmlhttprequest", "localstorage", "sessionstorage", "document.cookie"):
            with self.subTest(prohibited_api=prohibited_api):
                self.assertNotIn(prohibited_api, content)

    def test_web_guide_documents_standard_library_server_and_local_url(self) -> None:
        content = WEB_GUIDE.read_text(encoding="utf-8")

        self.assertIn("python -m http.server 8000", content)
        self.assertIn("http://localhost:8000/assets/demo-interactiva.html", content)
        self.assertIn("No requiere dependencias", content)


if __name__ == "__main__":
    unittest.main()
