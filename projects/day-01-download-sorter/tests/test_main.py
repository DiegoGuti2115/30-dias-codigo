"""Automated checks for the Day 1 download sorter."""

from __future__ import annotations

import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from main import sort_downloads


class DownloadSorterTests(unittest.TestCase):
    """Verify the documented happy path and safety behavior."""

    def test_sorts_known_files_and_preserves_safe_cases(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            known_files = {
                "imagen.png": "Imágenes",
                "documento.txt": "Documentos",
                "archivo.zip": "Comprimidos",
                "audio.wav": "Audio",
                "video.mp4": "Vídeo",
            }
            for filename in known_files:
                (root / filename).write_bytes(b"fixture")

            (root / "desconocido.xyz").write_text("unknown", encoding="utf-8")
            (root / "SIN_EXTENSION").write_text("no extension", encoding="utf-8")
            protected_directory = root / "Subcarpeta intacta"
            protected_directory.mkdir()
            protected_file = protected_directory / "contenido.txt"
            protected_file.write_text("protected", encoding="utf-8")
            (root / "Imágenes").mkdir()
            conflict_destination = root / "Imágenes" / "conflicto.png"
            conflict_destination.write_bytes(b"existing")
            (root / "conflicto.png").write_bytes(b"candidate")

            output = io.StringIO()
            results = sort_downloads(root, output)

            self.assertEqual(5, sum(result.status == "movido" for result in results))
            self.assertEqual(2, sum(result.status == "desconocido" for result in results))
            self.assertEqual(1, sum(result.status == "conflicto" for result in results))
            self.assertEqual(0, sum(result.status == "error" for result in results))
            for filename, category in known_files.items():
                self.assertTrue((root / category / filename).is_file())
                self.assertFalse((root / filename).exists())
            self.assertTrue((root / "desconocido.xyz").is_file())
            self.assertTrue((root / "SIN_EXTENSION").is_file())
            self.assertEqual("protected", protected_file.read_text(encoding="utf-8"))
            self.assertEqual(b"existing", conflict_destination.read_bytes())
            self.assertEqual(b"candidate", (root / "conflicto.png").read_bytes())
            self.assertIn("movidos=5", output.getvalue())
            self.assertIn("desconocidos=2", output.getvalue())
            self.assertIn("conflictos=1", output.getvalue())

            repeat_output = io.StringIO()
            repeat_results = sort_downloads(root, repeat_output)
            self.assertEqual(3, len(repeat_results))
            self.assertEqual(2, sum(result.status == "desconocido" for result in repeat_results))
            self.assertEqual(1, sum(result.status == "conflicto" for result in repeat_results))
            self.assertIn("movidos=0", repeat_output.getvalue())

    def test_rejects_an_invalid_input_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            missing_directory = Path(temporary_directory) / "missing"
            with self.assertRaises(ValueError):
                sort_downloads(missing_directory, io.StringIO())


if __name__ == "__main__":
    unittest.main()
