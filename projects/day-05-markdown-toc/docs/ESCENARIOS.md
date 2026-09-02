# Inventario de escenarios — Fase 2

Este inventario transforma el contrato v1 de [`CONTRATO.md`](CONTRATO.md) en datos sintéticos reproducibles. Es una referencia para las fases posteriores: no ejecuta pruebas ni introduce implementación en los módulos reservados.

## Convenciones de referencia

- Los documentos de entrada se guardan en [`data/fixtures`](../data/fixtures).
- Los resultados de extracción y de índice se guardan en [`data/expected`](../data/expected) como JSON UTF-8.
- Las vistas previas completas se guardan como Markdown y representan el documento resultante sin persistirlo.
- Los diagnósticos de bloque se centralizan en [`error-scenarios.json`](../data/expected/error-scenarios.json).
- Los números de línea se cuentan desde `1` y las profundidades de índice desde `0`.
- Las rutas inválidas, las extensiones no admitidas, enlaces simbólicos, permisos y UTF-8 inválido son condiciones del sistema de archivos. Se registran como cobertura prevista, sin crear recursos dependientes de la plataforma en esta fase.

## Escenarios de contenido y jerarquía

| Fixture | Cobertura contractual | Referencia | Resultado esperado |
|---|---|---|---|
| [`complex-valid.md`](../data/fixtures/complex-valid.md) | Encabezados ATX, jerarquía profunda, saltos consecutivos, Unicode, puntuación, duplicados, ancla de reserva, bloque obsoleto y código delimitado cerrado. | [`complex-valid.json`](../data/expected/complex-valid.json), [`complex-valid-preview.md`](../data/expected/complex-valid-preview.md) | Extrae seis encabezados, omite el código y reemplaza solo el interior del bloque. |
| [`atx-edge-cases.md`](../data/fixtures/atx-edge-cases.md) | Hasta tres espacios iniciales, cierre ATX, líneas no elegibles, guiones, espacios, enlace y código en línea literal. | [`atx-edge-cases.json`](../data/expected/atx-edge-cases.json) | Extrae únicamente cuatro encabezados elegibles y preserva literalmente sus etiquetas visibles. |
| [`fenced-code-unclosed.md`](../data/fixtures/fenced-code-unclosed.md) | Cerca insuficiente y bloque delimitado sin cierre. | [`fenced-code-unclosed.json`](../data/expected/fenced-code-unclosed.json) | Solo el encabezado anterior a la cerca es elegible; el resto queda excluido. |
| [`no-headings.md`](../data/fixtures/no-headings.md) | Documento válido sin encabezados elegibles y bloque válido. | [`no-headings-preview.md`](../data/expected/no-headings-preview.md) | El contenido interior del bloque queda vacío. |
| [`empty.md`](../data/fixtures/empty.md) | Documento vacío. | [`error-scenarios.json`](../data/expected/error-scenarios.json) | No hay bloque válido; se informa bloque ausente y no se escribe. |

## Escenarios de delimitadores

| Fixture | Condición | Diagnóstico esperado | Escritura |
|---|---|---|:---:|
| [`missing-block.md`](../data/fixtures/missing-block.md) | No contiene delimitadores. | Bloque de índice ausente. | No |
| [`incomplete-block.md`](../data/fixtures/incomplete-block.md) | Solo contiene inicio. | Bloque de índice incompleto. | No |
| [`inverted-block.md`](../data/fixtures/inverted-block.md) | El fin aparece antes del inicio. | Bloque de índice invertido. | No |
| [`duplicate-block.md`](../data/fixtures/duplicate-block.md) | Hay más de un par de delimitadores. | Bloque de índice duplicado. | No |
| [`invalid-marker.md`](../data/fixtures/invalid-marker.md) | El delimitador de inicio tiene espacio inicial. | Bloque de índice inválido. | No |

Las cinco referencias se consolidan en [`error-scenarios.json`](../data/expected/error-scenarios.json) con código de salida `1` y `write_permitted: false`.

## Cobertura de ruta, codificación y persistencia prevista

Estas condiciones no se materializan como fixtures portables porque dependen del sistema operativo, permisos o tipos de archivo. Las fases de pruebas e integración deberán cubrirlas con recursos temporales controlados:

| Condición del contrato | Resultado previsto |
|---|---|
| Ruta inexistente, directorio, enlace simbólico o extensión distinta de `.md` / `.markdown` | Error de entrada, código `1`, sin interpretación ni escritura. |
| Archivo sin permiso de lectura | Error de entrada, código `1`, sin interpretación ni escritura. |
| Archivo no decodificable como UTF-8 | Error de codificación, código `1`, sin interpretación ni escritura. |
| Archivo sin permiso de escritura con `--write` | Error de actualización, código `1`, original intacto. |
| Vista previa de un bloque válido | Código `0`, documento propuesto completo en salida estándar, archivo intacto. |
| Actualización válida | Código `0`, confirmación estable, sustitución limitada y preservación definida por el contrato. |

## Trazabilidad de criterios de aceptación de Fase 2

- **Cobertura de contrato:** los escenarios anteriores cubren gramática ATX, exclusión por código, anclas, jerarquía, bloque válido y todos los diagnósticos de delimitador.
- **Cambios detectables:** las referencias contienen líneas, niveles, textos, anclas, profundidades, índice y documentos de vista previa para revelar regresiones en transformación y preservación.
- **Datos sintéticos:** todos los títulos, textos y URLs usan contenido ficticio; no contienen secretos ni información personal.
- **Sin implementación:** [`src`](../src) y [`tests`](../tests) permanecen reservados y vacíos al cierre de esta fase.
