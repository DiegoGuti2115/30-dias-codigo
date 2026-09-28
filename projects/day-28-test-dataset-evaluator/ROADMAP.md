# Roadmap — Validador de datasets de evaluación

## Principios de evolución

El proyecto prioriza validaciones locales, deterministas y rápidas. Cada fase debe conservar el formato de informe documentado en [`README.md`](README.md) o versionarlo explícitamente. Las integraciones con evaluadores o servicios externos solo se considerarán cuando exista un fixture o adaptador local equivalente.

## Fase 0 — Base del proyecto ✅

**Prioridad: alta**

- Estructura `src/`, `tests/`, `data/`, `assets/`, `docs/` y `config/`.
- Contratos Pydantic para registros, hallazgos y reportes.
- CLI JSON local, informe JSON y ejemplos válidos/no válidos.
- Reglas iniciales: esquema mínimo, `id` único y advertencia por metadatos vacíos.
- Pruebas unitarias de la ruta principal.

**Criterio de salida:** instalar dependencias, validar [`data/examples/valid-dataset.json`](data/examples/valid-dataset.json) y ejecutar `python -m pytest` sin errores.

## Fase 1 — Configuración operativa y experiencia CLI ✅

**Prioridad: alta**

- Cargar y validar un archivo de configuración compatible con [`config/default.json`](config/default.json).
- Añadir códigos de salida estables para entrada inválida, errores de archivo y hallazgos de severidad error.
- Mejorar mensajes de JSON malformado y de rutas inexistentes.
- Añadir pruebas de argumentos CLI, configuración y límites de hallazgos.
- Documentar una tabla completa de códigos de salida y de error.

**Criterio de salida:** las opciones de [`ValidationSettings`](src/evaluation_dataset_validator/config/settings.py:8) se pueden modificar sin cambios de código.

## Fase 2 — Reglas de calidad del contenido ✅

**Prioridad: alta**

- Reglas configurables para entradas o salidas vacías cuando sean cadenas.
- Validación de campos de metadatos requeridos por tipo de tarea.
- Detección de duplicados semánticos simples mediante normalización local y huellas.
- Severidades por regla y posibilidad de deshabilitarlas.
- Fixtures que cubran límites, unicode y estructuras JSON anidadas.

**Criterio de salida:** toda regla nueva implementa [`ValidationRule`](src/evaluation_dataset_validator/rules/base.py:10), produce códigos documentados y tiene pruebas.

## Fase 3 — Formatos y reportes ✅

**Prioridad: media**

- [x] Adaptadores de entrada para JSONL y CSV con mapeo explícito a `DatasetRecord`.
- [x] Salida opcional en consola y SARIF/CSV, manteniendo JSON como formato canónico.
- [x] Referencias de línea, columna y archivo para cada hallazgo de origen.
- [x] Resúmenes por tipo de error, tarea y partición del dataset.
- [x] Pruebas de compatibilidad entre formatos y de serialización.

**Decisiones y límites:** CSV requiere las columnas `id`, `input` y `expected_output`; `metadata` acepta un objeto JSON o columnas con prefijo `metadata.`. Las ubicaciones JSON se expresan por índice de registro, mientras JSONL y CSV preservan su línea física. El informe JSON sigue siendo canónico y contiene los nuevos agregados sin romper sus campos existentes.

**Criterio de salida:** cumplido; los fixtures equivalentes JSON, JSONL y CSV producen el mismo resultado de validación y se prueban junto con las serializaciones CSV y SARIF.

## Fase 4 — Validación específica de evaluación de IA ✅

**Prioridad: media**

- [x] Esquemas versionados para tareas de texto, clasificación, extracción y conversación.
- [x] Comprobación de campos esperados según tipo de evaluador.
- [x] Validaciones de cobertura: clases, idiomas, categorías y particiones.
- [x] Reglas locales para detectar posibles fugas entre entrenamiento y evaluación mediante hashes configurables.
- [x] Documentación de limitaciones: estas reglas no sustituyen revisión humana ni evaluación estadística.

**Decisiones y límites:** un registro activa el contrato de fase 4 al declarar `metadata.task_schema`; así se conserva la compatibilidad con los datasets previos. La cobertura se limita a dimensiones explícitas de `metadata` y las fugas comparan hashes SHA-256 de valores configurados entre particiones declaradas, sin inferir similitud semántica.

**Criterio de salida:** cumplido; cada esquema tiene casos válidos e inválidos en [`data/examples/phase4-valid.json`](data/examples/phase4-valid.json) y [`data/examples/phase4-invalid.json`](data/examples/phase4-invalid.json), además de la guía [`docs/PHASE4_MIGRATION.md`](docs/PHASE4_MIGRATION.md).

## Fase 5 — Integraciones y automatización ✅

**Prioridad: baja**

- [x] Acción de CI y comando orientado a pre-commit.
- [x] Adaptador webhook opcional con publicación local equivalente.
- [x] Exportación de métricas JSON y Prometheus.
- [x] Modo local/fallback garantizado para toda integración externa.
- [x] Pruebas de contrato con publicadores locales, sin credenciales ni red.

**Decisiones y límites:** el webhook es HTTP mínimo y opcional; ante cualquier error se conserva la validación y se escribe un payload local. CI ejecuta la misma puerta local reproducible.

**Criterio de salida:** cumplido; el fallo de integración activa fallback local sin impedir validación ni pruebas reproducibles.

## Mejoras futuras por evaluar

- Autocorrecciones revisables para identificadores o metadatos derivados.
- Archivo de línea base para aceptar temporalmente hallazgos conocidos.
- API FastAPI y una interfaz web únicamente si el flujo CLI queda consolidado.
- Benchmarks de rendimiento para datasets de gran tamaño.
- Versionado formal del formato de informe.

## Mantenimiento continuo

En cada entrega se actualizarán [`README.md`](README.md), los ejemplos y las pruebas en el mismo cambio que la funcionalidad. Se evitarán secretos y cualquier dependencia cloud deberá documentar su fallback local antes de incorporarse.
