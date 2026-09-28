# Arquitectura

Las fases 1 a 5 conservan separadas la configuración, carga de datos, dominio, reglas, orquestación, persistencia y presentación de resultados. La fase 5 añade automatización e integraciones opcionales sin acoplar reglas de validación a CI, red o credenciales.

```text
CLI
 ├─ config/loader -> ValidationSettings
 ├─ services/dataset_loader -> SourceRecord (JSON | JSONL | CSV)
 └─ DatasetValidator -> DatasetRecord + reglas -> ValidationReport -> JSON canónico + consola/CSV/SARIF
```

## Responsabilidades

- [`main.py`](../src/evaluation_dataset_validator/main.py): interpreta argumentos, coordina dependencias y convierte errores controlados en códigos de salida.
- [`errors.py`](../src/evaluation_dataset_validator/errors.py): define [`ExitCode`](../src/evaluation_dataset_validator/errors.py:9) y excepciones de infraestructura estables.
- [`config/loader.py`](../src/evaluation_dataset_validator/config/loader.py): lee JSON de configuración, exige una raíz objeto y lo valida contra [`ValidationSettings`](../src/evaluation_dataset_validator/config/settings.py:8).
- [`config/settings.py`](../src/evaluation_dataset_validator/config/settings.py): contiene opciones de dominio sin acoplarlas a argumentos o rutas, incluidas reglas deshabilitadas, severidades por regla, metadatos requeridos por tarea, esquemas versionados, cobertura y huellas de fugas.
- [`services/dataset_loader.py`](../src/evaluation_dataset_validator/services/dataset_loader.py): adapta JSON, JSONL y CSV UTF-8 a `SourceRecord`; concentra la detección de formato, el mapeo CSV y los errores de sintaxis o forma.
- [`models/contracts.py`](../src/evaluation_dataset_validator/models/contracts.py): contratos Pydantic estables de entrada, ubicación de origen, hallazgos, resumen e informe.
- [`validators/dataset.py`](../src/evaluation_dataset_validator/validators/dataset.py): aplica esquema, reglas globales y reglas por registro; propaga la ubicación de origen y calcula agregados completos antes de limitar la lista mostrada de hallazgos.
- [`rules/`](../src/evaluation_dataset_validator/rules): punto de extensión para comprobaciones independientes. Cada implementación respeta el protocolo [`ValidationRule`](../src/evaluation_dataset_validator/rules/base.py:10).
- [`reporting/json_report.py`](../src/evaluation_dataset_validator/reporting/json_report.py): escribe el informe JSON canónico en UTF-8.
- [`reporting/formatters.py`](../src/evaluation_dataset_validator/reporting/formatters.py): proyecta el mismo informe hacia consola, CSV o SARIF 2.1.0 sin alterar el contrato canónico.
- [`reporting/metrics.py`](../src/evaluation_dataset_validator/reporting/metrics.py): deriva métricas JSON y Prometheus solo a partir de `ValidationReport`.
- [`integrations.py`](../src/evaluation_dataset_validator/integrations.py): aísla el webhook opcional detrás de `ReportPublisher` y persiste una proyección local si el adaptador falla.
- [`scripts/precommit_check.py`](../scripts/precommit_check.py): puerta local que CI ejecuta sin comportamientos específicos de plataforma.

## Reglas de calidad configurables

[`DatasetValidator`](../src/evaluation_dataset_validator/validators/dataset.py:25) construye las reglas integradas únicamente cuando [`ValidationSettings.is_rule_enabled()`](../src/evaluation_dataset_validator/config/settings.py:101) las habilita y les inyecta la severidad obtenida mediante [`ValidationSettings.severity_for()`](../src/evaluation_dataset_validator/config/settings.py:105). Así, [`config/default.json`](../config/default.json) puede desactivar una regla o convertir un hallazgo de `error` en `warning` sin modificar el código.

Las reglas de fase 2 son:

- [`EmptyStringRule`](../src/evaluation_dataset_validator/rules/content.py:12): detecta `input` o `expected_output` que sean cadenas vacías o contengan únicamente espacios.
- [`RequiredMetadataFieldsRule`](../src/evaluation_dataset_validator/rules/task_metadata.py:12): exige campos de `metadata` para el tipo indicado en `metadata.task`.
- [`SemanticDuplicateInputRule`](../src/evaluation_dataset_validator/rules/semantic_duplicates.py:13): localiza repeticiones de entradas de texto tras normalización Unicode NFKC, `casefold` y compactación de espacios; la huella SHA-256 se usa solo como comparación local y determinista.
- [`EmptyMetadataRule`](../src/evaluation_dataset_validator/rules/metadata.py:12): conserva la advertencia de trazabilidad para registros sin metadatos.

La comprobación de identificadores duplicados sigue siendo global, porque necesita observar todos los registros válidos. La regla semántica también se prepara a partir de la colección completa, pero solo evalúa texto: las entradas JSON anidadas se mantienen fuera de esa heurística para evitar equivalencias ambiguas.

## Contratos de evaluación y reglas globales

[`EvaluationTaskSchemaRule`](../src/evaluation_dataset_validator/rules/evaluation_tasks.py:15) se aplica exclusivamente a registros que declaran `metadata.task_schema`. Valida las versiones locales `text/v1`, `classification/v1`, `extraction/v1` y `conversation/v1`, además de su evaluador, tipo de salida y metadatos específicos. Esta activación explícita mantiene compatibilidad con datasets de fases previas.

[`CoverageRule`](../src/evaluation_dataset_validator/rules/evaluation_tasks.py:86) calcula ausencias declaradas para los cuatro ejes permitidos de `metadata` y aporta `missing_coverage` como hallazgo global. [`coverage_counts()`](../src/evaluation_dataset_validator/rules/evaluation_tasks.py:133) conserva los conteos observados en `ValidationSummary.coverage_by_field`, por lo que el informe JSON, CSV, SARIF y consola parten del mismo estado determinista.

[`TrainEvaluationLeakageRule`](../src/evaluation_dataset_validator/rules/evaluation_tasks.py:116) serializa canónicamente campos explícitamente configurados y compara sus hashes SHA-256 entre particiones. No realiza similitud semántica ni sustituye una auditoría de procedencia. La guía detallada y los límites están en [`PHASE4_MIGRATION.md`](PHASE4_MIGRATION.md).

## Formatos, ubicaciones y salidas

Los adaptadores devuelven [`SourceRecord`](../src/evaluation_dataset_validator/services/dataset_loader.py:22), que asocia el payload normalizado a [`SourceLocation`](../src/evaluation_dataset_validator/models/contracts.py:18). JSON comunica la posición lógica del registro dentro del array; JSONL y CSV conservan la línea física, con la columna inicial `1`.

CSV mantiene un mapeo deliberadamente explícito: necesita `id`, `input` y `expected_output`; los metadatos proceden de una columna `metadata` con objeto JSON o de columnas `metadata.<campo>`. Los valores de `input` y `expected_output` con apariencia de array u objeto se decodifican localmente cuando son JSON válido.

[`ValidationSummary`](../src/evaluation_dataset_validator/models/contracts.py:58) conserva los contadores base y suma agrupaciones por código, tarea y partición. Los formatos opcionales solo proyectan los hallazgos expuestos por `max_issues`; el JSON canónico se escribe siempre y conserva el informe completo hasta ese mismo límite de presentación.

## Flujo y límites

La CLI no captura errores de programación ni introduce efectos secundarios al importar módulos. Solo los errores previsibles derivados de archivos, JSON, configuración o estructura de entrada se traducen en mensajes consistentes y códigos documentados en [`README.md`](../README.md). Si el dataset llega a validarse, el informe se escribe incluso cuando contiene hallazgos de severidad `error`; los errores anteriores a la validación no generan informes parciales.

`max_issues` limita únicamente `issues`. Los contadores de `summary` y `is_valid` se derivan de todos los hallazgos detectados, para que el estado de la ejecución no dependa de la presentación. El informe serializado conserva el contrato [`ValidationReport`](../src/evaluation_dataset_validator/models/contracts.py:70), independientemente de las reglas activadas.

## Automatización e integraciones

La CLI escribe primero el informe JSON canónico y las salidas seleccionadas. Después puede generar métricas JSON/Prometheus y, de forma opcional, enviar esa proyección a un webhook. [`publish_with_fallback()`](../src/evaluation_dataset_validator/integrations.py:61) atrapa fallos de infraestructura del publicador, escribe el mismo payload en [`LocalReportPublisher`](../src/evaluation_dataset_validator/integrations.py:24) y deja intacto el código de salida asociado al resultado de validación.

La automatización no usa una dependencia de red: el workflow [`ci.yml`](../.github/workflows/ci.yml) ejecuta la misma puerta que el desarrollador mediante [`precommit_check.py`](../scripts/precommit_check.py). Las pruebas sustituyen el protocolo de publicación con un fixture local que falla controladamente.
