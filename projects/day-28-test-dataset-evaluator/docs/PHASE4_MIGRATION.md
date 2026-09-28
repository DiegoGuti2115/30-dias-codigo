# Guía de migración — esquemas de evaluación de IA

La fase 4 es optativa y compatible con datasets de fases anteriores: un registro solo activa la validación específica cuando declara [`metadata.task_schema`](../src/evaluation_dataset_validator/models/contracts.py:26). Los esquemas son locales, versionados y no requieren modelos ni servicios externos.

## Migrar un registro

1. Añada `metadata.task_schema` con una de las versiones admitidas.
2. Añada `metadata.evaluator` compatible con ese esquema.
3. Complete los metadatos específicos indicados abajo.
4. Configure cobertura o detección de fugas solo si el dataset declara las dimensiones y particiones correspondientes.

| Esquema | Evaluador | `input` | `expected_output` | Metadatos adicionales |
|---|---|---|---|---|
| `text/v1` | `exact_match` o `contains` | texto | texto | — |
| `classification/v1` | `label_match` | cualquier JSON | etiqueta de `label_set` | `label_set` no vacío |
| `extraction/v1` | `field_match` | cualquier JSON | objeto o lista | `extraction_fields` no vacío |
| `conversation/v1` | `turn_match` | lista de `{role, content}` | texto | — |

## Ejemplos válidos e inválidos

### Texto

```json
{"id":"text-ok","input":"Resume.","expected_output":"Resumen.","metadata":{"task_schema":"text/v1","evaluator":"exact_match"}}
{"id":"text-bad","input":"Resume.","expected_output":"Resumen.","metadata":{"task_schema":"text/v1","evaluator":"label_match"}}
```

### Clasificación

```json
{"id":"class-ok","input":"Excelente","expected_output":"positive","metadata":{"task_schema":"classification/v1","evaluator":"label_match","label_set":["positive","negative"]}}
{"id":"class-bad","input":"Excelente","expected_output":"neutral","metadata":{"task_schema":"classification/v1","evaluator":"label_match","label_set":["positive","negative"]}}
```

### Extracción

```json
{"id":"extract-ok","input":"Ana vive en Madrid.","expected_output":{"person":"Ana"},"metadata":{"task_schema":"extraction/v1","evaluator":"field_match","extraction_fields":["person"]}}
{"id":"extract-bad","input":"Ana vive en Madrid.","expected_output":"Ana","metadata":{"task_schema":"extraction/v1","evaluator":"field_match","extraction_fields":[]}}
```

### Conversación

```json
{"id":"chat-ok","input":[{"role":"user","content":"Hola"}],"expected_output":"Hola","metadata":{"task_schema":"conversation/v1","evaluator":"turn_match"}}
{"id":"chat-bad","input":[{"role":"user"}],"expected_output":"Hola","metadata":{"task_schema":"conversation/v1","evaluator":"turn_match"}}
```

Los conjuntos completos están en [`phase4-valid.json`](../data/examples/phase4-valid.json) y [`phase4-invalid.json`](../data/examples/phase4-invalid.json).

## Cobertura y fugas

`coverage_required_values` declara valores mínimos para `metadata.class`, `metadata.language`, `metadata.category` y `metadata.partition`. El informe conserva los conteos observados en `summary.coverage_by_field` y emite `missing_coverage` si falta algún valor requerido.

`leakage_hash_fields` habilita comparación exacta SHA-256 entre las particiones de entrenamiento y evaluación. Admite `input`, `expected_output` y `metadata.source_id`; su serialización JSON canónica garantiza resultados deterministas para objetos y listas. Los hallazgos `train_evaluation_leakage` se asignan al registro de evaluación que coincide.

## Límites

Estas reglas son comprobaciones estructurales y heurísticas locales. No sustituyen la revisión humana de etiquetas, la auditoría de sesgos, el análisis estadístico de cobertura ni una investigación de procedencia. Una coincidencia de hash señala reutilización exacta de un valor configurado, no una fuga semántica completa; la ausencia de una coincidencia tampoco demuestra independencia entre particiones.
