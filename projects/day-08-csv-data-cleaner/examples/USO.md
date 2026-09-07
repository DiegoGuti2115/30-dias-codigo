# Uso local reproducible

Ejecuta todos los comandos desde [`projects/day-08-csv-data-cleaner`](..). Solo se necesita Python 3.11+ y la biblioteca estándar; no se instala ningún paquete ni se usa red, credenciales o secretos.

## 1. Flujo feliz y comparación de referencias

Crea un directorio de salida nuevo. La CLI no crea directorios padre ni sobrescribe archivos existentes.

```text
mkdir tmp
python src/main.py clean data/fixtures/happy-input.csv data/fixtures/plan-all-operations.json tmp/happy-cleaned.csv tmp/happy-summary.json
```

El comando debe devolver `0`, escribir las dos rutas finales en stdout y crear:

- `tmp/happy-cleaned.csv`, idéntico a [`data/expected/happy-cleaned.csv`](../data/expected/happy-cleaned.csv).
- `tmp/happy-summary.json`, equivalente a [`data/expected/happy-summary.json`](../data/expected/happy-summary.json).

Comprueba ambas referencias y que el origen sigue idéntico:

```text
python -c "from pathlib import Path; import json; source=Path('data/fixtures/happy-input.csv'); before=source.read_bytes(); assert Path('tmp/happy-cleaned.csv').read_bytes() == Path('data/expected/happy-cleaned.csv').read_bytes(); assert json.loads(Path('tmp/happy-summary.json').read_text(encoding='utf-8')) == json.loads(Path('data/expected/happy-summary.json').read_text(encoding='utf-8')); assert source.read_bytes() == before; print('References and source preservation verified.')"
```

## 2. Caso válido sin cambios

```text
python src/main.py clean data/fixtures/no-changes-input.csv data/fixtures/plan-no-changes.json tmp/no-changes-cleaned.csv tmp/no-changes-summary.json
```

También devuelve `0`. Las operaciones son válidas aunque todos sus contadores sean `0`.

## 3. Error esperado sin publicación

Este comando usa un plan inválido y debe devolver `1`, escribir el diagnóstico seguro `plan_unsupported_version` en stderr y no crear las dos salidas:

```text
python src/main.py clean data/fixtures/happy-input.csv data/fixtures/invalid-plan-version.json tmp/error-cleaned.csv tmp/error-summary.json
```

La única sintaxis admitida es:

```text
python src/main.py clean <SOURCE_CSV> <PLAN_JSON> <OUTPUT_CSV> <SUMMARY_JSON>
```

- Forma de comando inválida: stderr y código `2`.
- CSV, plan, ruta, límite o publicación no admisible: stderr y código `1`.
- Éxito: stdout y código `0` solo después de publicar ambos artefactos.

La herramienta no muestra valores de celdas, no modifica el origen, no sobrescribe salidas y no autodetecta dialectos. Un punto y coma dentro de un campo sigue siendo contenido válido bajo el dialecto contractual de coma.

## 4. Limpieza

Elimina solo el directorio creado para esta guía:

```text
rmdir /s /q tmp
```
