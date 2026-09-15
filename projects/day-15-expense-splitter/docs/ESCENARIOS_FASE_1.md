# Catálogo de escenarios — Fase 1

Este catálogo traduce [CONTRATO_V1.md](CONTRATO_V1.md) en vectores documentales para las fases de implementación y prueba. No es un fixture ejecutable, no necesita un entorno TypeScript y no adelanta código de cálculo.

## Convenciones

- Todos los ejemplos son documentos JSON conceptuales con datos sintéticos.
- Los importes están expresados en unidades menores de la moneda indicada.
- `OK` significa que el futuro cálculo debe emitir el resultado exacto descrito.
- `ERROR` significa que debe emitirse el código público documentado; la implementación podrá indicar una ruta más precisa conforme al contrato.
- Los balances se muestran ordenados por `participantId`; las transferencias siguen el algoritmo de liquidación de [CONTRATO_V1.md](CONTRATO_V1.md).

## Reparto igualitario y redondeo

| ID   | Participantes y gasto                                                                                                    | Estado | Resultado esperado                                                                                                                                  | Regla cubierta                             |
| ---- | ------------------------------------------------------------------------------------------------------------------------ | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| R-01 | `ana`, `bruno`; 100 pagado por `ana`, compartido por ambos                                                               | OK     | Ana: pagó 100, debe 50, balance `50`; Bruno: pagó 0, debe 50, balance `-50`; transferencia `bruno → ana: 50`                                        | División exacta.                           |
| R-02 | `ana`, `bruno`, `carla`; 1001 pagado por `ana`, compartido en orden `ana`, `bruno`, `carla`                              | OK     | Cuotas: Ana `334`, Bruno `334`, Carla `333`; balances: Ana `667`, Bruno `-334`, Carla `-333`; transferencias `bruno → ana: 334`, `carla → ana: 333` | Resto distribuido por orden.               |
| R-03 | `ana`, `bruno`, `carla`; 5 pagado por `ana`, compartido en orden `carla`, `bruno`, `ana`                                 | OK     | Cuotas: Carla `2`, Bruno `2`, Ana `1`; balances: Ana `4`, Bruno `-2`, Carla `-2`; transferencias `bruno → ana: 2`, `carla → ana: 2`                 | El orden de `splitAmong` es significativo. |
| R-04 | `ana`, `bruno`; 300 pagado por `ana`, compartido solo por `bruno`                                                        | OK     | Ana: pagó `300`, debe `0`, balance `300`; Bruno: debe `300`, balance `-300`; transferencia `bruno → ana: 300`                                       | El pagador puede no participar.            |
| R-05 | `ana`, `bruno`; gasto de 200 pagado por Ana y compartido por ambos; gasto de 200 pagado por Bruno y compartido por ambos | OK     | Ambos balances `0`; `transfers` vacío                                                                                                               | Posición saldada.                          |

## Acumulación y orden de transferencias

| ID   | Datos resumidos                                                                                                   | Estado | Resultado esperado                                                                                            | Regla cubierta                                          |
| ---- | ----------------------------------------------------------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| B-01 | `ana`, `bruno`, `carla`; gastos: 900 pagado por Ana para los tres y 300 pagado por Bruno para Bruno y Carla       | OK     | Balances: Ana `600`, Bruno `-150`, Carla `-450`; transferencias `bruno → ana: 150`, `carla → ana: 450`        | Acumulación por persona y orden ascendente de deudores. |
| B-02 | `ana`, `bruno`, `carla`, `david`; balances finales calculados: Ana `500`, Bruno `200`, Carla `-300`, David `-400` | OK     | Transferencias `carla → ana: 300`, `david → ana: 200`, `david → bruno: 200`                                   | Emparejamiento determinista por `participantId`.        |
| B-03 | Cualquier documento válido                                                                                        | OK     | La suma de `balanceMinor` es `0`; la suma de transferencias recibidas menos enviadas deja cada balance en `0` | Conservación monetaria.                                 |

## Documento válido mínimo

| ID   | Documento conceptual                                                                                         | Estado | Resultado esperado                                                                                                                    |
| ---- | ------------------------------------------------------------------------------------------------------------ | ------ | ------------------------------------------------------------------------------------------------------------------------------------- |
| V-01 | `version: "v1"`, `currency: "EUR"`, participantes `ana` y `bruno`, un gasto válido de 1 compartido por ambos | OK     | El importe completo se asigna: Ana, primera en `splitAmong`, debe `1`; Bruno debe `0`. La suma de cuotas y balances permanece exacta. |
| V-02 | Dos participantes con el mismo `name` pero distintos `id` y un gasto válido                                  | OK     | El documento es válido; los nombres no se usan como referencia ni se deduplican.                                                      |
| V-03 | Moneda `USD`, mismos importes enteros y modelo válido                                                        | OK     | El cálculo es idéntico al de otra moneda; `currency` se conserva como `USD` sin conversión ni formato.                                |

## Errores de validación

| ID   | Condición                                                                       | Estado | Código esperado                                                 | Regla cubierta                        |
| ---- | ------------------------------------------------------------------------------- | ------ | --------------------------------------------------------------- | ------------------------------------- |
| E-01 | Raíz no objeto, clave raíz adicional o falta una clave obligatoria              | ERROR  | `E_VALIDATION_ROOT` o `E_VALIDATION_UNKNOWN_FIELD`              | Gramática raíz cerrada.               |
| E-02 | `version` distinta de `v1`                                                      | ERROR  | `E_VALIDATION_VERSION`                                          | Versión cerrada.                      |
| E-03 | `currency` no coincide con `^[A-Z]{3}$`                                         | ERROR  | `E_VALIDATION_CURRENCY`                                         | Moneda declarada.                     |
| E-04 | Menos de dos participantes, más de 50 o lista no array                          | ERROR  | `E_VALIDATION_PARTICIPANTS`                                     | Cardinalidad de participantes.        |
| E-05 | Sin gastos, más de 500 o lista no array                                         | ERROR  | `E_VALIDATION_EXPENSES`                                         | Cardinalidad de gastos.               |
| E-06 | Identificador de participante o gasto duplicado                                 | ERROR  | `E_VALIDATION_DUPLICATE_ID`                                     | Identificadores únicos.               |
| E-07 | `id`, `name` o `description` vacío tras recorte, o `id` con patrón no permitido | ERROR  | `E_VALIDATION_TEXT`                                             | Texto e identificadores válidos.      |
| E-08 | `amountMinor` es cadena, decimal, cero, negativo o entero inseguro              | ERROR  | `E_VALIDATION_AMOUNT`                                           | Unidades menores positivas y seguras. |
| E-09 | `paidBy` no corresponde a un participante                                       | ERROR  | `E_VALIDATION_UNKNOWN_PARTICIPANT`                              | Pagador referenciado.                 |
| E-10 | `splitAmong` vacío, no array, contiene repetidos o una referencia desconocida   | ERROR  | `E_VALIDATION_SPLIT_AMONG` o `E_VALIDATION_UNKNOWN_PARTICIPANT` | Participantes de reparto explícitos.  |
| E-11 | Participante o gasto contiene una clave no declarada                            | ERROR  | `E_VALIDATION_UNKNOWN_FIELD`                                    | Objetos cerrados.                     |

## Errores de interfaz futura

| ID   | Invocación conceptual                                              | Estado | Salida esperada           | Error esperado                    | Código |
| ---- | ------------------------------------------------------------------ | ------ | ------------------------- | --------------------------------- | :----: |
| C-01 | `expense-splitter ./data/fixtures/viaje.json` con documento válido | OK     | Un resultado JSON         | Vacía                             |  `0`   |
| C-02 | `expense-splitter --help`                                          | OK     | Ayuda exacta del contrato | Vacía                             |  `0`   |
| C-03 | `expense-splitter`                                                 | ERROR  | Vacía                     | `E_USAGE_ARGUMENTS`               |  `2`   |
| C-04 | `expense-splitter uno.json dos.json`                               | ERROR  | Vacía                     | `E_USAGE_ARGUMENTS`               |  `2`   |
| C-05 | `expense-splitter --formato json`                                  | ERROR  | Vacía                     | `E_USAGE_UNKNOWN_OPTION`          |  `2`   |
| C-06 | Ruta no accesible, no regular o no UTF-8                           | ERROR  | Vacía                     | Código `E_INPUT_*` aplicable      |  `3`   |
| C-07 | Archivo UTF-8 con JSON malformado                                  | ERROR  | Vacía                     | `E_INPUT_JSON_PARSE`              |  `3`   |
| C-08 | Archivo JSON válido que incumple el modelo                         | ERROR  | Vacía                     | Código `E_VALIDATION_*` aplicable |  `4`   |

## Trazabilidad para fases posteriores

- La Fase 2 podrá preparar el entorno sin modificar reglas ni vectores de este documento.
- La Fase 3 deberá cubrir `R-*`, `B-*`, `V-*` y `E-*` mediante pruebas del núcleo puro.
- La Fase 4 deberá implementar las invocaciones y separación de canales definidas en `C-*`.
- La Fase 5 deberá automatizar los escenarios relevantes y comprobar determinismo, conservación de importes, salida estándar, salida de error y códigos de proceso.
- Cualquier modificación de un vector requiere actualizar el contrato y justificarla en [DECISIONES.md](DECISIONES.md).
