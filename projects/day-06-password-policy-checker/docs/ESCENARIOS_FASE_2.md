# Escenarios sintéticos y referencias — Fase 2

## Propósito

Este inventario transforma el contrato v1 en escenarios verificables sin incorporar contraseñas, fragmentos de contraseñas, longitudes reales de entradas evaluadas ni salidas de CLI. Las etiquetas describen únicamente categorías, condiciones y resultados esperados.

Los metadatos están separados en [`data/fixtures/scenario-catalog.json`](../data/fixtures/scenario-catalog.json) y las referencias en [`data/expected/scenario-results.json`](../data/expected/scenario-results.json). Ambos archivos son declarativos y no ejecutables.

## Estrategia de inyección efímera

Las pruebas construyen, dentro del proceso y solo durante cada caso, una cadena que satisfaga las categorías y longitudes abstractas del catálogo. Esa cadena no se persiste en archivos, nombres de pruebas, snapshots, mensajes de aserción, diagnósticos ni resultados esperados.

Las categorías del catálogo se interpretan según [`CONTRATO.md`](CONTRATO.md):

- `uppercase`, `lowercase`, `decimal-digit` y `special` representan los cuatro requisitos de categoría de la política.
- `unicode-*` verifica la clasificación Unicode de Python.
- `combining-mark` representa caracteres combinantes que cuentan para longitud y no satisfacen una categoría por sí mismos.
- `whitespace` es una condición adicional, evaluada después de las cinco reglas principales.

## Trazabilidad

| Escenario | Requisito contractual | Referencia esperada |
|---|---|---|
| `all-rules-satisfied` | Política válida completa. | Estado global válido y cinco reglas satisfechas. |
| `length-below-minimum` | Límite inferior inclusivo. | Solo falla `length`. |
| `missing-uppercase` | Mayúscula Unicode obligatoria. | Solo falla `uppercase`. |
| `missing-lowercase` | Minúscula Unicode obligatoria. | Solo falla `lowercase`. |
| `missing-decimal-digit` | Dígito decimal Unicode obligatorio. | Solo falla `digit`. |
| `missing-special` | Carácter especial permitido obligatorio. | Solo falla `special`. |
| `combined-failures` | Evaluación completa, sin cortocircuito. | Fallos múltiples en orden estable. |
| `empty-input` | Entrada vacía evaluable. | Las cinco reglas fallan. |
| `minimum-length` | Longitud mínima incluida. | Resultado válido. |
| `maximum-length` | Longitud máxima incluida. | Resultado válido. |
| `above-maximum-length` | Longitud superior al máximo. | Solo falla `length`. |
| `unicode-categories` | Clasificación Unicode sin normalización. | Resultado válido. |
| `combining-marks-only` | Combinantes sin categoría propia. | Solo cumple `length`. |
| `whitespace-present` | Espacio en blanco invalida tras reglas principales. | Cinco reglas satisfechas y `has_whitespace` verdadero. |

## Referencias de salida y retorno

La Fase 2 no crea una CLI, pero reserva las expectativas contractuales para fases posteriores:

- Un resultado válido tendrá código de retorno `0`.
- Un resultado evaluado no válido tendrá código `1`.
- Errores de argumentos tendrán código `2`.
- Fallos de interacción segura tendrán código `1`.
- La salida futura mantendrá el orden `length`, `uppercase`, `lowercase`, `digit`, `special`; el diagnóstico de espacios aparecerá después.

## Revisión de privacidad

- Los archivos de esta fase no contienen contraseñas reales, recomendables ni reutilizables.
- No incluyen caracteres concretos utilizados por pruebas, posiciones, hashes, longitudes de una entrada real ni datos de identidad.
- Las referencias registran estados booleanos y metadatos de política, no valores evaluados.
- La implementación y las pruebas de fases posteriores deben conservar esta estrategia de valores efímeros.
