# Día 28 — Validador de datasets de evaluación

> Microproyecto del reto **30 Días, 30 Proyectos**: una CLI local que valida estructura, trazabilidad y calidad básica de datasets JSON, JSONL y CSV antes de utilizarlos para evaluar sistemas de IA.

## Propósito y alcance

Un `id` duplicado, una cadena vacía, metadatos incompletos o una entrada repetida pueden degradar métricas y dificultar resultados reproducibles. La herramienta trabaja de forma local, determinista, rápida y sin credenciales ni servicios externos.

La fase 4 conserva las reglas configurables, los formatos y los informes de las fases anteriores, y añade:

- Esquemas locales y versionados para texto, clasificación, extracción y conversación.
- Comprobación del evaluador y de los campos esperados por cada tipo de tarea.
- Cobertura configurable por clase, idioma, categoría y partición, con conteos deterministas en el informe.
- Detección local de posibles fugas entre entrenamiento y evaluación mediante hashes SHA-256 de campos configurados.
- Fixtures válidos e inválidos y una guía de migración para cada esquema de tarea.

La fase 5 conserva la validación local como ruta principal y añade una puerta reproducible de CI/pre-commit, métricas JSON/Prometheus y un webhook opcional con fallback local. No ejecuta modelos, prompts ni evaluadores automáticos; tampoco usa credenciales ni requiere servicios externos para validar o probar.

## Arquitectura

```text
CLI -> config/loader -> ValidationSettings
CLI -> services/dataset_loader (JSON|JSONL|CSV) -> DatasetValidator -> reglas -> ValidationReport -> JSON canónico + salidas opcionales
```

- [`main.py`](src/evaluation_dataset_validator/main.py): argumentos, códigos de salida y mensajes de usuario.
- [`config/loader.py`](src/evaluation_dataset_validator/config/loader.py): lectura y validación de configuración JSON.
- [`config/settings.py`](src/evaluation_dataset_validator/config/settings.py): opciones y políticas de reglas.
- [`services/dataset_loader.py`](src/evaluation_dataset_validator/services/dataset_loader.py): adaptadores y mapeo controlado de JSON, JSONL y CSV.
- [`validators/dataset.py`](src/evaluation_dataset_validator/validators/dataset.py): orquestación de esquema, reglas, ubicaciones de origen y resúmenes agregados.
- [`models/contracts.py`](src/evaluation_dataset_validator/models/contracts.py): contratos Pydantic de entrada, ubicaciones, hallazgos e informe.
- [`rules/content.py`](src/evaluation_dataset_validator/rules/content.py), [`rules/task_metadata.py`](src/evaluation_dataset_validator/rules/task_metadata.py) y [`rules/semantic_duplicates.py`](src/evaluation_dataset_validator/rules/semantic_duplicates.py): reglas nuevas de fase 2.
- [`reporting/json_report.py`](src/evaluation_dataset_validator/reporting/json_report.py): salida JSON canónica.
- [`reporting/formatters.py`](src/evaluation_dataset_validator/reporting/formatters.py): renderizadores opcionales de consola, CSV y SARIF.
- [`reporting/metrics.py`](src/evaluation_dataset_validator/reporting/metrics.py): proyección local del resumen hacia JSON y Prometheus.
- [`integrations.py`](src/evaluation_dataset_validator/integrations.py): webhook opcional y fallback local aislado.
- [`scripts/precommit_check.py`](scripts/precommit_check.py): puerta reproducible para desarrollo local y CI.

La descripción ampliada está en [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Formato de entrada

El formato se detecta por extensión (`.json`, `.jsonl`/`.ndjson` o `.csv`) o se fija con `--input-format`. Todos los adaptadores producen el mismo contrato. JSON usa un **array JSON** y JSONL un objeto JSON por línea no vacía. CSV exige encabezados y las columnas siguientes:

| Campo | Tipo | Obligatorio | Descripción |
|---|---|:---:|---|
| `id` | cadena no vacía | Sí | Identificador estable del caso. |
| `input` | cualquier valor JSON | Sí | Entrada enviada al sistema evaluado. Las cadenas vacías se validan por regla. |
| `expected_output` | cualquier valor JSON | Sí | Resultado esperado. Las cadenas vacías se validan por regla. |
| `metadata` | objeto JSON | No | Contexto de trazabilidad y, opcionalmente, tipo de tarea. |

En CSV, `metadata` puede ser un objeto JSON serializado o distribuirse en columnas con prefijo `metadata.`. Los ejemplos equivalentes de fase 3 están en [`data/examples/phase3-compatible.json`](data/examples/phase3-compatible.json), [`data/examples/phase3-compatible.jsonl`](data/examples/phase3-compatible.jsonl) y [`data/examples/phase3-compatible.csv`](data/examples/phase3-compatible.csv). Los ejemplos base y de calidad se mantienen en [`data/examples/valid-dataset.json`](data/examples/valid-dataset.json), [`data/examples/invalid-dataset.json`](data/examples/invalid-dataset.json), [`data/examples/quality-valid-dataset.json`](data/examples/quality-valid-dataset.json) y [`data/examples/quality-invalid-dataset.json`](data/examples/quality-invalid-dataset.json).

## Configuración

La CLI carga [`config/default.json`](config/default.json) por defecto. Puede sustituirse con `--config`.

| Opción | Tipo | Efecto |
|---|---|---|
| `required_fields` | array fijo | Debe contener `id`, `input` y `expected_output`. |
| `require_unique_ids` | booleano | Activa `duplicate_id`. |
| `warn_on_empty_metadata` | booleano | Activa la regla heredada `empty_metadata`. |
| `detect_semantic_duplicates` | booleano | Activa `semantic_duplicate_input`. |
| `metadata_required_fields_by_task` | objeto | Mapa `{ "tarea": ["campo"] }`; se aplica cuando `metadata.task` coincide. |
| `disabled_rules` | array | Nombres de reglas que se omiten de la ejecución. |
| `supported_task_schemas` | array | Esquemas admitidos: `text/v1`, `classification/v1`, `extraction/v1` y `conversation/v1`. |
| `coverage_required_values` | objeto | Valores obligatorios para `metadata.class`, `metadata.language`, `metadata.category` o `metadata.partition`. |
| `leakage_hash_fields` | array | Campos a comparar entre entrenamiento y evaluación: `input`, `expected_output` o `metadata.source_id`. Vacío lo desactiva. |
| `leakage_train_partitions` | array | Etiquetas que se consideran entrenamiento (por defecto `train`). |
| `leakage_evaluation_partitions` | array | Etiquetas de evaluación (por defecto `validation`, `test`, `evaluation`). |
| `rule_severities` | objeto | Sobrescrituras `"error"` o `"warning"` por regla; las no indicadas conservan su valor predeterminado. |
| `max_issues` | entero ≥ 1 | Limita solo los elementos expuestos en `issues`. |

Los nombres configurables de regla son `unique_id`, `empty_metadata`, `empty_input`, `empty_expected_output`, `required_metadata_fields`, `semantic_duplicate_input`, `evaluation_task_schema`, `coverage` y `train_evaluation_leakage`. Claves desconocidas, reglas inexistentes, tareas/campos vacíos y valores incompatibles generan `CONFIG_ERROR`.

### Normalización de duplicados semánticos

Solo se comparan valores de `input` que sean cadenas no vacías. La comparación normaliza Unicode con NFKC, aplica `casefold`, comprime espacios y calcula una huella SHA-256 local. Por ello `"  ¡HOLA   MUNDO! "` y `"¡hola mundo!"` se consideran duplicados. Las estructuras JSON anidadas se ignoran deliberadamente para evitar inferencia semántica fuera del alcance de esta fase.

## Reglas y formato del informe

El formato JSON se conserva: `is_valid`, `summary` e `issues`. Cada hallazgo contiene `code`, `message`, `severity`, `record_id`, `field`, `rule` y `location` con `file`, `line` y `column`. `summary` incorpora `issues_by_code`, `issues_by_task` e `issues_by_partition`; los campos previos se mantienen sin cambios.

| Código | Regla | Severidad predeterminada | Criterio |
|---|---|---|---|
| `invalid_schema` | `schema` | error | Faltan campos obligatorios, `id` es vacío o `metadata` no es objeto. |
| `duplicate_id` | `unique_id` | error | Un mismo `id` aparece más de una vez. |
| `empty_metadata` | `empty_metadata` | warning | Un registro válido no contiene metadatos. |
| `empty_input` | `empty_input` | error | `input` es una cadena vacía o solo contiene espacios. |
| `empty_expected_output` | `empty_expected_output` | error | `expected_output` es una cadena vacía o solo contiene espacios. |
| `missing_required_metadata` | `required_metadata_fields` | error | Falta o está vacío un campo requerido para `metadata.task`. |
| `semantic_duplicate_input` | `semantic_duplicate_input` | warning | Una entrada textual coincide con una entrada previa tras normalización. |
| `unsupported_task_schema` | `evaluation_task_schema` | error | `metadata.task_schema` no es una versión soportada. |
| `invalid_evaluator` | `evaluation_task_schema` | error | El evaluador no corresponde al esquema de tarea. |
| `invalid_evaluation_schema` | `evaluation_task_schema` | error | Faltan campos o tipos específicos del esquema. |
| `missing_coverage` | `coverage` | warning | Falta un valor configurado de cobertura. |
| `train_evaluation_leakage` | `train_evaluation_leakage` | warning | Una huella configurada coincide entre entrenamiento y evaluación. |

`is_valid` es `false` si se detecta al menos un hallazgo `error`, incluso si `max_issues` oculta parte de la lista. Cambiar una severidad a `warning` puede mantener el dataset válido sin ocultar el hallazgo.

## Instalación y uso

Requiere Python 3.11+.

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m pip install -e .
```

Se conserva la interfaz como módulo:

```bash
python -m evaluation_dataset_validator.main data/examples/phase3-compatible.jsonl --output-format console
```

También está disponible el comando instalado:

```bash
evaluation-dataset-validator data/examples/phase3-compatible.csv --report output/report.json --output-format csv --output output/report.csv
```

`--report` siempre escribe JSON. Para obtener SARIF, use `--output-format sarif --output output/report.sarif`; si no se indica `--output`, se usa el nombre de `--report` con extensión `.sarif` o `.csv`. `--output` requiere exactamente una salida adicional no JSON.

Para comprobar cobertura y fugas con los ejemplos de fase 4:

```bash
python -m evaluation_dataset_validator.main data/examples/phase4-invalid.json --config config/phase4-verification.json --report output/phase4-report.json --output-format sarif --output output/phase4-report.sarif
```

El comando anterior finaliza con `1`, conserva el informe JSON y genera SARIF; su configuración reproducible está en [`config/phase4-verification.json`](config/phase4-verification.json).

### Automatización, métricas e integración opcional

La puerta local (también ejecutada por CI) es:

```bash
python scripts/precommit_check.py
```

Para exportar métricas sin dependencias externas:

```bash
python -m evaluation_dataset_validator.main data/examples/phase4-valid.json --metrics-format prometheus --metrics-output output/validation.prom
```

`--metrics-format` acepta `json` y `prometheus`; las rutas derivadas desde `--report` son `.metrics.json` y `.prom`. `--metrics-output` requiere exactamente un formato. El webhook es opcional y siempre mantiene fallback local:

```bash
python -m evaluation_dataset_validator.main data/examples/phase4-valid.json --publish-webhook http://127.0.0.1:1/unavailable --publish-fallback output/fallback.json
```

Si el webhook falla, el informe y el código de salida de validación se conservan, y el payload de métricas se escribe en el fallback. La guía completa está en [`docs/AUTOMATION.md`](docs/AUTOMATION.md).

## Códigos de salida

| Código | Nombre | Estado |
|---:|---|---|
| 0 | `SUCCESS` | Validación ejecutada sin hallazgos de error. |
| 1 | `VALIDATION_ERRORS` | Se escribió el informe, pero contiene uno o más errores. |
| 2 | `INVALID_INPUT` | Dataset malformado, formato no detectable, mapeo CSV incompleto o uso inválido de argumentos. |
| 3 | `FILE_ERROR` | No se puede leer dataset/configuración o escribir informe. |
| 4 | `CONFIG_ERROR` | Configuración JSON inválida o incompatible. |

Los errores se muestran como `Error: ...` sin trazas internas y no generan informes parciales.

## Pruebas y criterio de aceptación

```bash
python -m pytest
```

La suite cubre carga y configuración, compatibilidad de fase 1, reglas de cadenas vacías, metadatos por tarea, unicode, entradas anidadas, duplicados semánticos, severidades, reglas deshabilitadas, límite de hallazgos, JSONL, CSV, ubicaciones de origen, agregados, SARIF, CLI, métricas, automatización y fallbacks de integración.

La fase 4 se acepta cuando cada esquema tiene ejemplos válidos e inválidos, la configuración controla cobertura y fugas reproducibles, y [`docs/PHASE4_MIGRATION.md`](docs/PHASE4_MIGRATION.md) permite migrar un registro existente.

Las validaciones de fase 4 son comprobaciones locales de estructura, cobertura declarada y coincidencias exactas. No sustituyen revisión humana, auditorías de sesgo ni evaluación estadística.

## Documentación relacionada

- [`ROADMAP.md`](ROADMAP.md): fases futuras y límites de alcance.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): responsabilidades de módulos.
- [`docs/PHASE4_MIGRATION.md`](docs/PHASE4_MIGRATION.md): contratos versionados, ejemplos y migración de fase 4.
- [`docs/AUTOMATION.md`](docs/AUTOMATION.md): CI, pre-commit, métricas, webhook y fallback de fase 5.
- [`../../README.md`](../../README.md): registro global del reto.
