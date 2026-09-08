"""Phase 6 delivery-artifact checks for the local portfolio API."""

from __future__ import annotations

from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class DeliveryDocumentationTests(unittest.TestCase):
    """Keep local delivery documentation aligned with the implemented read-only v1."""

    def test_phase_six_delivery_artifacts_are_present(self) -> None:
        required_files = (
            PROJECT_ROOT / "README.md",
            PROJECT_ROOT / "ROADMAP.md",
            PROJECT_ROOT / "docs" / "CONTRATO_API_V1.md",
            PROJECT_ROOT / "docs" / "VERIFICACION_FASE_5.md",
            PROJECT_ROOT / "docs" / "VERIFICACION_FASE_6.md",
            PROJECT_ROOT / "examples" / "RESPUESTAS_PLANIFICADAS.md",
            PROJECT_ROOT / "examples" / "USO_HTTP_LOCAL.md",
            PROJECT_ROOT / "assets" / "DEMO_15S.md",
        )

        for path in required_files:
            with self.subTest(path=path.relative_to(PROJECT_ROOT)):
                self.assertTrue(path.is_file())

    def test_delivery_guides_keep_the_verified_local_read_only_scope(self) -> None:
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
        verification = (PROJECT_ROOT / "docs" / "VERIFICACION_FASE_6.md").read_text(encoding="utf-8")
        usage = (PROJECT_ROOT / "examples" / "USO_HTTP_LOCAL.md").read_text(encoding="utf-8")
        demo = (PROJECT_ROOT / "assets" / "DEMO_15S.md").read_text(encoding="utf-8")

        self.assertIn("--app-dir src", readme)
        self.assertIn("sys.path.insert(0, 'src')", readme)
        self.assertIn("openapi-read-only: ok", verification)
        self.assertIn("/api/v1/projects/Portfolio-API", verification)
        self.assertIn("project_not_found", usage)
        self.assertIn("15 segundos", demo)

        for document in (readme, verification, usage, demo):
            with self.subTest(document=document[:30]):
                self.assertIn("GET", document)
                self.assertNotIn("POST /api/v1", document)
                self.assertNotIn("https://api.", document)

    def test_project_has_no_environment_or_generated_delivery_artifacts(self) -> None:
        forbidden_patterns = (".env", "*.db", "*.sqlite", "demo-tmp")

        for pattern in forbidden_patterns:
            with self.subTest(pattern=pattern):
                self.assertFalse(list(PROJECT_ROOT.rglob(pattern)))


if __name__ == "__main__":
    unittest.main()
