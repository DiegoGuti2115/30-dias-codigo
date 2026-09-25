"""Tests for the command-line validation, extraction, and result flow."""

import json
from pathlib import Path

from document_splitter.main import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_OVERLAP,
    main,
    parse_args,
)


def test_parse_args_uses_documented_defaults() -> None:
    """The scaffold exposes the documented chunking defaults."""
    arguments = parse_args([])

    assert arguments.source is None
    assert arguments.chunk_size == DEFAULT_CHUNK_SIZE
    assert arguments.overlap == DEFAULT_OVERLAP
    assert arguments.output is None


def test_parse_args_accepts_the_future_processing_contract() -> None:
    """Source, sizing, overlap, and output are accepted without processing."""
    arguments = parse_args(
        [
            "data/input/manual.pdf",
            "--chunk-size",
            "800",
            "--overlap",
            "100",
            "--output",
            "output/manual.json",
        ]
    )

    assert arguments.source == Path("data/input/manual.pdf")
    assert arguments.chunk_size == 800
    assert arguments.overlap == 100
    assert arguments.output == Path("output/manual.json")


def test_main_returns_success_when_no_source_is_requested() -> None:
    """The help-compatible invocation still succeeds without a source path."""
    assert main([]) == 0


def test_main_writes_a_traceable_result_for_a_supported_source(
    tmp_path: Path, capsys: object
) -> None:
    """A valid source is normalized, fragmented, and persisted as requested."""
    source = tmp_path / "notas.txt"
    destination = tmp_path / "resultado.json"
    source.write_text("contenido", encoding="utf-8")

    assert (
        main(
            [
                str(source),
                "--chunk-size",
                "200",
                "--overlap",
                "20",
                "--output",
                str(destination),
            ]
        )
        == 0
    )
    captured = capsys.readouterr()
    assert "Documento fragmentado correctamente: 1 fragmentos." in captured.out
    assert f"Salida: {destination.resolve()}" in captured.out
    payload = json.loads(destination.read_text(encoding="utf-8"))
    assert payload["source"] == "notas.txt"
    assert payload["chunks"] == [
        {
            "id": f"{payload['document_id']}-0",
            "index": 0,
            "text": "contenido",
            "start_char": 0,
            "end_char": 9,
        }
    ]


def test_main_rejects_an_existing_output_file(tmp_path: Path, capsys: object) -> None:
    """The CLI does not overwrite a result produced by another execution."""
    source = tmp_path / "notas.txt"
    destination = tmp_path / "resultado.json"
    source.write_text("contenido", encoding="utf-8")
    destination.write_text("resultado previo", encoding="utf-8")

    assert main([str(source), "--output", str(destination)]) == 4
    captured = capsys.readouterr()
    assert "Error de resultado" in captured.err
    assert "ya existe" in captured.err
    assert destination.read_text(encoding="utf-8") == "resultado previo"


def test_main_processes_the_documented_txt_fixture_end_to_end(
    tmp_path: Path, capsys: object
) -> None:
    """The documented fixture produces a readable, ordered JSON result."""
    fixture = Path(__file__).parent / "fixtures" / "sample.txt"
    destination = tmp_path / "sample-result.json"

    assert main([str(fixture), "--chunk-size", "30", "--overlap", "5", "--output", str(destination)]) == 0
    captured = capsys.readouterr()
    payload = json.loads(destination.read_text(encoding="utf-8"))

    assert "Documento fragmentado correctamente" in captured.out
    assert payload["source"] == "sample.txt"
    assert [chunk["index"] for chunk in payload["chunks"]] == list(
        range(len(payload["chunks"]))
    )
    assert "Primera linea." in " ".join(chunk["text"] for chunk in payload["chunks"])
    assert "Segunda linea en orden." in " ".join(
        chunk["text"] for chunk in payload["chunks"]
    )


def test_main_returns_validation_exit_code_and_message(
    tmp_path: Path, capsys: object
) -> None:
    """Invalid input has a stable non-zero CLI outcome."""
    missing_source = tmp_path / "ausente.txt"

    assert main([str(missing_source)]) == 2
    captured = capsys.readouterr()
    assert "Error de validación" in captured.err
    assert "no existe" in captured.err


def test_main_returns_extraction_exit_code_and_message(
    tmp_path: Path, capsys: object
) -> None:
    source = tmp_path / "corrupto.pdf"
    source.write_text("esto no es un PDF", encoding="utf-8")
    assert main([str(source)]) == 3
    captured = capsys.readouterr()
    assert "Error de extracción" in captured.err
    assert "No se pudo extraer texto" in captured.err
