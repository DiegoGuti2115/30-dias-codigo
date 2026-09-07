# Escenarios, fixtures y referencias — Fase 2

## Propósito y estado

Este inventario convierte el contrato v1 de [`CONTRATO.md`](CONTRATO.md) en casos trazables, sintéticos y reproducibles. Define entradas, planes y referencias que las fases posteriores implementaron y verifican sin reinterpretar requisitos.

Los módulos de [`src/`](../src) y las pruebas de [`tests/`](../tests) implementan ahora el núcleo, la CLI y la publicación. Las condiciones dependientes del sistema de archivos se crean de forma efímera en las pruebas para conservar la portabilidad.

El catálogo declarativo se encuentra en [`data/fixtures/scenario-catalog.json`](../data/fixtures/scenario-catalog.json). Los CSV y planes de entrada están en [`data/fixtures`](../data/fixtures); los resultados estables de transformaciones correctas y los errores esperados se encuentran en [`data/expected`](../data/expected).

## Convenciones de fixtures y referencias

- Todos los CSV utilizan UTF-8 sin BOM, delimitador de coma, comillas CSV estándar y terminador LF, salvo el fixture binario creado para representar una codificación inválida.
- Los nombres de encabezado, textos y valores son sintéticos e inocuos. No hay personas reales, secretos, credenciales, rutas de máquina ni datos de producción.
- Las referencias JSON se serializan en UTF-8, con indentación de dos espacios y claves ordenadas alfabéticamente. Esta es la representación adoptada por la publicación del resumen.
- Las referencias solo describen estructura, encabezados, contadores, operaciones y códigos; nunca contienen filas de datos fuera de los CSV sintéticos ni contenido que la CLI deba mostrar.
- Los escenarios de permisos, interrupción y fallo de publicación se construyen en directorios temporales aislados. No se versionan artefactos dependientes de permisos, enlaces, antivirus o concurrencia de Windows.

## Matriz de trazabilidad

| Escenario | Fixture / condición | Referencia | RF cubiertos | Resultado contractual |
|---|---|---|---|---|
| `happy-all-operations` | [`happy-input.csv`](../data/fixtures/happy-input.csv) + [`plan-all-operations.json`](../data/fixtures/plan-all-operations.json) | [`happy-cleaned.csv`](../data/expected/happy-cleaned.csv), [`happy-summary.json`](../data/expected/happy-summary.json) | RF-01 a RF-09 | Éxito determinista; cinco operaciones, dos artefactos publicados y origen intacto. |
| `valid-no-changes` | [`no-changes-input.csv`](../data/fixtures/no-changes-input.csv) + [`plan-no-changes.json`](../data/fixtures/plan-no-changes.json) | [`no-changes-cleaned.csv`](../data/expected/no-changes-cleaned.csv), [`no-changes-summary.json`](../data/expected/no-changes-summary.json) | RF-02, RF-03, RF-05, RF-07, RF-09 | Operaciones válidas sin cambios; contadores a cero. |
| `header-normalization-collision` | [`header-collision-input.csv`](../data/fixtures/header-collision-input.csv) + [`plan-normalize-headers.json`](../data/fixtures/plan-normalize-headers.json) | [`error-scenarios.json`](../data/expected/error-scenarios.json) | RF-01, RF-04, RF-06, RF-08 | Plan incompatible; rechazo antes de cualquier salida. |
| `invalid-plan-shapes` | Planes `invalid-plan-*.json` | [`error-scenarios.json`](../data/expected/error-scenarios.json) | RF-03, RF-04, RF-08 | Error de plan, sin perfil publicado ni salidas. |
| `missing-source` | Ruta temporal inexistente | [`error-scenarios.json`](../data/expected/error-scenarios.json) | RF-01, RF-06, RF-08 | Error de entrada, código `1`, sin efectos. |
| `comma-only-dialect` | Todos los CSV correctos del catálogo | Referencias CSV y JSON correctas | RF-01, RF-09 | Lectura solo con delimitador coma y sin autodetección; no se aceptan modos alternativos. |
| `unsupported-encoding` | [`invalid-utf8-input.csv`](../data/fixtures/invalid-utf8-input.csv) | [`error-scenarios.json`](../data/expected/error-scenarios.json) | RF-01, RF-08 | Error de entrada por decodificación no UTF-8. |
| `malformed-csv` | [`malformed-input.csv`](../data/fixtures/malformed-input.csv) | [`error-scenarios.json`](../data/expected/error-scenarios.json) | RF-01, RF-08 | Error de sintaxis CSV, sin publicación. |
| `empty-or-irregular-csv` | [`empty-input.csv`](../data/fixtures/empty-input.csv) o [`irregular-input.csv`](../data/fixtures/irregular-input.csv) | [`error-scenarios.json`](../data/expected/error-scenarios.json) | RF-01, RF-08 | Error de encabezado o de cardinalidad de fila. |
| `resource-limits` | Archivo/filas/columnas generados efímeramente | [`error-scenarios.json`](../data/expected/error-scenarios.json) | RF-01, RF-08 | Error de límite, sin salidas. |
| `conflicting-output-routes` | Rutas temporales iguales, existentes o peligrosas | [`error-scenarios.json`](../data/expected/error-scenarios.json) | RF-06, RF-08 | Rechazo previo a transformación/publicación. |
| `permission-or-publication-failure` | Permiso revocado o fallo de escritura inyectado | [`error-scenarios.json`](../data/expected/error-scenarios.json) | RF-06, RF-07, RF-08 | Código `1`; origen intacto, ninguna salida presentada como completa. |
| `repeated-identical-run` | Dos ejecuciones temporales con `happy-all-operations` | [`happy-cleaned.csv`](../data/expected/happy-cleaned.csv), [`happy-summary.json`](../data/expected/happy-summary.json) | RF-05, RF-07, RF-09 | Mismo contenido de resultados en cada ejecución aislada. |

## Detalle del flujo feliz

`happy-all-operations` cubre las cinco operaciones en su orden contractual:

1. `normalize_headers` transforma `" Display Name "` en `"Display Name"`.
2. `drop_empty_rows` elimina una fila formada por tres cadenas vacías del CSV de origen.
3. `trim_fields` modifica seis campos de las filas aún presentes.
4. `replace_missing_markers` convierte dos marcadores explícitos en cadenas vacías.
5. `drop_exact_duplicates` elimina la segunda fila de `Ben,,ready`, que solo se vuelve duplicada después de los pasos anteriores.

El fixture también incluye una celda que empieza por `=`. Las referencias confirman el recuento agregado de una celda similar a fórmula y la advertencia correspondiente, sin cambiar su contenido.

## Planes inválidos y compatibilidad

| Archivo | Motivo de rechazo |
|---|---|
| [`invalid-plan-extra-root.json`](../data/fixtures/invalid-plan-extra-root.json) | Clave adicional en la raíz. |
| [`invalid-plan-unknown-operation.json`](../data/fixtures/invalid-plan-unknown-operation.json) | Operación fuera de la lista cerrada. |
| [`invalid-plan-duplicate-operation.json`](../data/fixtures/invalid-plan-duplicate-operation.json) | Operación repetida. |
| [`invalid-plan-empty-markers.json`](../data/fixtures/invalid-plan-empty-markers.json) | Lista de marcadores vacía. |
| [`invalid-plan-version.json`](../data/fixtures/invalid-plan-version.json) | Versión distinta de `1`. |
| [`plan-normalize-headers.json`](../data/fixtures/plan-normalize-headers.json) con `header-collision-input.csv` | Colisión de encabezados después del recorte. |

No se crea un fixture de punto y coma que deba rechazarse por inspección de contenido. Con el dialecto contractual de coma, una línea sin comas como `label;status` es un CSV válido de una sola columna cuyo valor contiene `;`; rechazarla requeriría autodetección o una restricción adicional no aprobada por [`CONTRATO.md`](CONTRATO.md). La cobertura del dialecto configura explícitamente el lector con coma, sin autodetección ni soporte alternativo.

## Cobertura dependiente de plataforma

Las fases de núcleo, CLI y publicación deberán crear estas condiciones solo en recursos temporales:

| Condición | Resultado esperado |
|---|---|
| Origen o plan inexistente, directorio o no legible | Error seguro, código `1`, ninguna salida. |
| Salida existente, directorio padre inexistente/no directorio, salida igual a origen/plan/otra salida o enlace | Rechazo antes de leer, transformar o crear temporales. |
| Más de 10 MiB, 10 000 filas de datos o 100 columnas | Rechazo según el punto de detección; ninguna salida final. |
| Permiso de salida denegado, interrupción o fallo inyectado al publicar | Origen y plan intactos; eliminar solo temporales propios si existen; código `1`. |
| Argumentos o subcomando inválidos | Error de uso, código `2`, ninguna salida. |

## Resultado de trazabilidad

- Cada RF-01 a RF-09 tiene al menos un escenario en la matriz.
- Se distinguen éxito, rechazo previo a publicación y fallo durante publicación.
- Los dos casos correctos fijan CSV limpio, resumen JSON, orden y métricas deterministas.
- Los fixtures se limitan a datos pequeños, sintéticos e inocuos.
- La implementación y las pruebas posteriores conservan estas referencias como oráculo de regresión.
