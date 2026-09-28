"""Pruebas de errores controlados al cargar datasets JSON."""

import pytest

from evaluation_dataset_validator.errors import ExitCode, FileAccessError, InvalidDatasetError, InvalidJsonError
from evaluation_dataset_validator.services.dataset_loader import load_json_dataset


def test_loads_json_array(tmp_path) -> None:
    source = tmp_path / "dataset.json"
    source.write_text('[{"id": "case-001"}]', encoding="utf-8")

    assert load_json_dataset(source) == [{"id": "case-001"}]


def test_reports_missing_dataset_file(tmp_path) -> None:
    with pytest.raises(FileAccessError) as captured:
        load_json_dataset(tmp_path / "missing.json")

    assert captured.value.exit_code is ExitCode.FILE_ERROR
    assert "No se puede leer el archivo" in str(captured.value)


def test_reports_malformed_json_with_location(tmp_path) -> None:
    source = tmp_path / "dataset.json"
    source.write_text("[", encoding="utf-8")

    with pytest.raises(InvalidJsonError) as captured:
        load_json_dataset(source)

    assert captured.value.exit_code is ExitCode.INVALID_INPUT
    assert "línea 1" in str(captured.value)


def test_rejects_non_array_root(tmp_path) -> None:
    source = tmp_path / "dataset.json"
    source.write_text('{"id": "case-001"}', encoding="utf-8")

    with pytest.raises(InvalidDatasetError) as captured:
        load_json_dataset(source)

    assert captured.value.exit_code is ExitCode.INVALID_INPUT
