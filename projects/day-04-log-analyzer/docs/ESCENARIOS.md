# Escenarios de fixtures — Fase 2

## Propósito

Este inventario convierte los criterios de aceptación de [`CONTRATO.md`](CONTRATO.md) en entradas sintéticas y resultados de referencia. Los fixtures no contienen datos personales, credenciales ni eventos de producción. Los archivos de `data/expected/` describen resultados estructurados para las fases 3 y 4; no fijan todavía el formato literal de terminal, cuya implementación corresponde a las fases 4 y 5.

## Convenciones de referencia

- `total_lines` cuenta todas las líneas físicas, incluidas las vacías.
- `valid_events` incluye únicamente eventos que cumplen completamente el contrato.
- `invalid_lines` cuenta cada línea que no puede normalizarse, sin exponer su contenido en una futura salida CLI.
- `level_counts` siempre enumera los cinco niveles v1 en su orden de severidad.
- `top_messages` se limita a tres elementos y desempata por primera aparición en el archivo.
- `error_line_numbers` conserva el orden físico y contiene solo eventos `ERROR` o `CRITICAL` válidos.
- Los archivos sin eventos válidos no tienen resumen de referencia: deben producir el error y código de salida `1` definidos en [`CONTRATO.md`](CONTRATO.md).

## Inventario

| Fixture | Formato | Escenarios cubiertos | Referencia |
|---|---|---|---|
| [`common-valid.log`](../data/fixtures/common-valid.log) | `common` | Cinco niveles, dos errores repetidos, Unicode y mensaje con espacios. | [`common-valid-summary.json`](../data/expected/common-valid-summary.json) |
| [`common-invalid.log`](../data/fixtures/common-invalid.log) | `common` | Línea vacía, alias `WARN`, mensaje ausente y timestamp no ISO 8601, entre dos eventos válidos. | [`common-invalid-summary.json`](../data/expected/common-invalid-summary.json) |
| [`common-all-invalid.log`](../data/fixtures/common-all-invalid.log) | `common` | Archivo no vacío sin eventos admisibles. | Error de análisis, código `1`. |
| [`jsonl-valid.jsonl`](../data/fixtures/jsonl-valid.jsonl) | `jsonl` | Cinco niveles, normalización de mayúsculas/minúsculas, metadatos adicionales y mensaje repetido. | [`jsonl-valid-summary.json`](../data/expected/jsonl-valid-summary.json) |
| [`jsonl-invalid.jsonl`](../data/fixtures/jsonl-invalid.jsonl) | `jsonl` | JSON malformado, nivel no admitido, campo obligatorio ausente, timestamp vacío, valor que no es objeto y línea vacía. | [`jsonl-invalid-summary.json`](../data/expected/jsonl-invalid-summary.json) |
| [`empty.log`](../data/fixtures/empty.log) | `common` o `jsonl` | Archivo vacío. | Error de análisis, código `1`. |

## Decisiones de Fase 2

- Los archivos de referencia son JSON estructurado para que las pruebas de análisis puedan comparar datos sin depender prematuramente del diseño de salida de terminal.
- Los errores de ruta, permisos, argumentos y codificación UTF-8 se probarán con archivos temporales y llamadas de proceso en las fases 3, 5 y 6; no se añaden artefactos específicos porque dependen del sistema operativo o requieren archivos binarios intencionalmente no UTF-8.
- No se añade ningún fixture de formatos externos ni de multilinea: ambos están fuera del contrato v1.

## Uso posterior

La fase 3 deberá utilizar los fixtures para probar que cada parser emite un evento normalizado o un diagnóstico por cada línea. La fase 4 utilizará los archivos de `data/expected/` para validar agregaciones, el orden de mensajes frecuentes y la selección de errores. La fase 5 validará que la CLI respete los códigos de salida documentados sobre estos mismos archivos.
