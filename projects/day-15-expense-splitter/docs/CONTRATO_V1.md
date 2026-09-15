# Contrato v1 — Divisor de gastos

## Estado y autoridad

Este documento cierra las decisiones funcionales de la Fase 1 de [ROADMAP.md](../ROADMAP.md) y será la fuente de verdad para las fases posteriores. No contiene una implementación, un manifiesto npm, fixtures ejecutables ni pruebas automatizadas.

- **Versión de contrato:** `v1`.
- **Interfaz prevista:** CLI local `expense-splitter`.
- **Entrada:** un único archivo JSON UTF-8 indicado de manera explícita.
- **Salida correcta:** un único documento JSON UTF-8 por salida estándar.
- **Salida de error:** un único documento JSON UTF-8 por salida de error.
- **Estado:** sin persistencia, red, cuentas, telemetría, secretos ni variables de entorno.
- **Compatibilidad:** cualquier cambio incompatible en la gramática, cálculos, redondeo, salida o códigos requerirá una versión posterior del contrato.

## Propósito, garantía y límites

La utilidad futura calcula cómo se divide un conjunto de gastos entre participantes y devuelve el balance neto de cada persona, junto con transferencias deterministas que permiten saldar esos balances.

Un resultado correcto garantiza únicamente que la entrada proporcionada cumple este contrato y que los importes se han repartido y redondeado según sus reglas. No certifica pagos reales, saldos bancarios, identidad de las personas, tipos de cambio, obligaciones fiscales ni acuerdos entre participantes.

La versión 1 no modifica el archivo de entrada, no guarda grupos ni historial, no solicita confirmaciones, no incorpora autenticación, no integra pagos, no consulta red ni servicios externos y no carga datos implícitos desde el directorio, variables de proceso o entrada estándar.

## Interfaz de línea de comandos

La interfaz futura admite exclusivamente estas formas:

```text
expense-splitter <ruta-entrada.json>
expense-splitter --help
expense-splitter -h
```

| Invocación                                                        | Salida estándar      | Salida de error           | Código |
| ----------------------------------------------------------------- | -------------------- | ------------------------- | :----: |
| Una ruta válida con datos válidos                                 | Resultado JSON       | Vacía                     |  `0`   |
| `--help` o `-h` aislado                                           | Ayuda de texto plano | Vacía                     |  `0`   |
| Sin ruta, más de una ruta, ayuda combinada u opción no reconocida | Vacía                | Error JSON de uso         |  `2`   |
| Archivo no accesible, no regular, no UTF-8 o JSON malformado      | Vacía                | Error JSON de entrada     |  `3`   |
| JSON interpretable que incumple el modelo v1                      | Vacía                | Error JSON de validación  |  `4`   |
| Fallo interno controlable                                         | Vacía                | Error JSON interno seguro |  `1`   |

La ruta se interpreta exactamente como argumento recibido y puede ser relativa al directorio de trabajo. La herramienta no descubre archivos por sí misma. Los diagnósticos públicos no incluirán rutas absolutas, contenido de archivos ni trazas.

La ayuda estable será:

```text
Uso: expense-splitter <ruta-entrada.json>

Calcula balances y transferencias de un reparto igualitario de gastos.
Ejemplo: expense-splitter ./data/fixtures/viaje.json
```

## Archivo de entrada JSON v1

El archivo se lee como texto UTF-8. Se podrá aceptar un BOM UTF-8 y eliminarlo antes de interpretar el documento; cualquier secuencia UTF-8 no válida será un error `E_INPUT_NOT_UTF8`.

El documento debe ser JSON estricto: no admite comentarios, comas finales ni formatos alternativos. Su raíz es un objeto con exactamente las claves siguientes:

| Clave          | Tipo   | Obligatoria | Regla                                                          |
| -------------- | ------ | :---------: | -------------------------------------------------------------- |
| `version`      | cadena |     Sí      | Debe ser exactamente `"v1"`.                                   |
| `currency`     | cadena |     Sí      | Código ISO 4217 ASCII de tres letras mayúsculas, `^[A-Z]{3}$`. |
| `participants` | lista  |     Sí      | Entre 2 y 50 participantes.                                    |
| `expenses`     | lista  |     Sí      | Entre 1 y 500 gastos.                                          |

No se admiten claves adicionales en la raíz, en participantes ni en gastos. Las claves se comparan con sensibilidad a mayúsculas y minúsculas.

### Participantes

Cada elemento de `participants` es un objeto con exactamente estas claves:

| Clave  | Tipo   | Obligatoria | Regla                                                                                 |
| ------ | ------ | :---------: | ------------------------------------------------------------------------------------- |
| `id`   | cadena |     Sí      | Identificador estable de 1 a 64 caracteres y patrón `^[A-Za-z0-9][A-Za-z0-9_-]*$`.    |
| `name` | cadena |     Sí      | Texto visible de 1 a 100 unidades UTF-16 tras recorte Unicode; no puede quedar vacío. |

Los identificadores deben ser únicos por comparación exacta. Los nombres no tienen que ser únicos y se conservan únicamente para presentar resultados; las referencias de gastos usan siempre `id`.

### Gastos

Cada elemento de `expenses` es un objeto con exactamente estas claves:

| Clave         | Tipo             | Obligatoria | Regla                                                                                 |
| ------------- | ---------------- | :---------: | ------------------------------------------------------------------------------------- |
| `id`          | cadena           |     Sí      | Identificador estable de 1 a 64 caracteres y patrón `^[A-Za-z0-9][A-Za-z0-9_-]*$`.    |
| `description` | cadena           |     Sí      | Texto visible de 1 a 200 unidades UTF-16 tras recorte Unicode; no puede quedar vacío. |
| `amountMinor` | número           |     Sí      | Entero seguro mayor que `0`; importe expresado en unidades menores de `currency`.     |
| `paidBy`      | cadena           |     Sí      | `id` de un participante declarado.                                                    |
| `splitAmong`  | lista de cadenas |     Sí      | Entre 1 y 50 identificadores de participantes declarados, sin repetidos.              |

Los identificadores de gasto deben ser únicos. El orden de `participants`, `expenses` y cada `splitAmong` forma parte de la entrada y se utiliza para el reparto de restos descrito más adelante.

Ejemplo exclusivamente documental:

```json
{
  "version": "v1",
  "currency": "EUR",
  "participants": [
    { "id": "ana", "name": "Ana" },
    { "id": "bruno", "name": "Bruno" },
    { "id": "carla", "name": "Carla" }
  ],
  "expenses": [
    {
      "id": "cena",
      "description": "Cena",
      "amountMinor": 1001,
      "paidBy": "ana",
      "splitAmong": ["ana", "bruno", "carla"]
    }
  ]
}
```

El ejemplo contiene datos sintéticos, no fija una persistencia y no autoriza campos adicionales.

## Moneda, importes y redondeo

Todos los importes se expresan como enteros en unidades menores de la moneda declarada: por ejemplo, céntimos para una moneda que use dos decimales. La herramienta no interpreta números decimales, no formatea importes para una configuración regional y no convierte divisas.

Para cada gasto de importe `amountMinor` y `n` participantes en `splitAmong`:

1. Se calcula `base = floor(amountMinor / n)`.
2. Se calcula `remainder = amountMinor % n`.
3. Cada participante recibe inicialmente una cuota de `base`.
4. Las primeras `remainder` personas de `splitAmong`, en el orden recibido, reciben una unidad menor adicional.

Esta regla distribuye siempre el importe completo, evita fracciones y es determinista. Un participante puede pagar un gasto y no figurar en `splitAmong`; no se añade implícitamente a la lista.

## Cálculo de balances y transferencias

La futura implementación procesará gastos en el orden recibido y aplicará estos valores enteros:

- `paid[participantId]`: suma de gastos cuyo `paidBy` coincide con la persona.
- `owed[participantId]`: suma de cuotas asignadas a la persona por `splitAmong`.
- `balanceMinor`: `paid - owed`.

Un balance positivo representa crédito; uno negativo representa deuda; cero indica posición saldada. La suma de todos los balances debe ser exactamente cero.

La salida v1 incluirá transferencias sugeridas para liquidar balances. Se generarán sobre las personas con balance no nulo, ordenando acreedores y deudores por `participantId` ascendente. En cada paso se empareja el primer deudor con el primer acreedor y se propone el mínimo entre la deuda absoluta y el crédito. Si uno queda saldado, se avanza al siguiente; si ambos quedan saldados, se avanza en ambas listas. Este algoritmo produce una secuencia determinista, aunque no pretende optimizar el número global de transferencias en todos los casos.

## Resultado JSON correcto

Cuando la entrada sea válida, la salida tendrá exactamente esta forma:

```json
{
  "version": "v1",
  "currency": "EUR",
  "totalMinor": 1001,
  "balances": [
    {
      "participantId": "ana",
      "name": "Ana",
      "paidMinor": 1001,
      "owedMinor": 334,
      "balanceMinor": 667
    }
  ],
  "transfers": [
    {
      "from": "bruno",
      "to": "ana",
      "amountMinor": 333
    }
  ]
}
```

- `totalMinor` es la suma de todos los gastos.
- `balances` se ordena por `participantId` ascendente e incluye a cada participante, incluso con balance cero.
- `transfers` usa el orden del algoritmo de liquidación; si no hay balances no nulos, es una lista vacía.
- Todos los importes son enteros seguros no negativos salvo `balanceMinor`, que puede ser negativo.
- La suma de `balanceMinor` es cero y cada transferencia tiene importe entero estrictamente positivo.

## Errores públicos

Todo fallo se serializa con esta forma:

```json
{
  "error": {
    "code": "E_VALIDATION_UNKNOWN_PARTICIPANT",
    "category": "validation",
    "message": "Los datos no cumplen el contrato v1.",
    "issues": [
      {
        "code": "E_VALIDATION_UNKNOWN_PARTICIPANT",
        "path": "expenses[0].paidBy",
        "message": "El participante referenciado no existe."
      }
    ]
  }
}
```

La implementación futura podrá acumular todas las incidencias determinables y deberá ordenarlas por `path` y después por `code`. Los mensajes de incidencia son estables, breves y no incluyen valores de entrada.

| Categoría    | Códigos posibles                                                                                                                                                                                                                                                                                  | Mensaje principal estable                    |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| `usage`      | `E_USAGE_ARGUMENTS`, `E_USAGE_UNKNOWN_OPTION`                                                                                                                                                                                                                                                     | `La invocación no cumple el uso esperado.`   |
| `input`      | `E_INPUT_READ`, `E_INPUT_NOT_REGULAR`, `E_INPUT_NOT_UTF8`, `E_INPUT_JSON_PARSE`                                                                                                                                                                                                                   | `No se pudo preparar el archivo de entrada.` |
| `validation` | `E_VALIDATION_ROOT`, `E_VALIDATION_UNKNOWN_FIELD`, `E_VALIDATION_VERSION`, `E_VALIDATION_CURRENCY`, `E_VALIDATION_PARTICIPANTS`, `E_VALIDATION_EXPENSES`, `E_VALIDATION_DUPLICATE_ID`, `E_VALIDATION_TEXT`, `E_VALIDATION_AMOUNT`, `E_VALIDATION_UNKNOWN_PARTICIPANT`, `E_VALIDATION_SPLIT_AMONG` | `Los datos no cumplen el contrato v1.`       |
| `internal`   | `E_INTERNAL`                                                                                                                                                                                                                                                                                      | `No se pudo calcular el reparto.`            |

## Validaciones y casos límite

- El documento requiere al menos dos participantes y un gasto.
- Los arrays, objetos y campos adicionales se rechazan donde no estén declarados.
- Un `id` vacío, con patrón inválido o duplicado se rechaza.
- Un nombre o descripción vacío tras recorte Unicode se rechaza; el valor visible se conservará como fue proporcionado, salvo el recorte usado para validarlo.
- `amountMinor` debe ser un número JSON entero seguro estrictamente positivo; no se aceptan cadenas, decimales, cero, negativos, `null`, `NaN` ni infinito.
- `paidBy` y cada entrada de `splitAmong` deben referenciar un participante declarado.
- `splitAmong` debe contener al menos una referencia y no puede repetir un `id`.
- Un gasto puede repartir su importe entre una sola persona y el pagador puede no ser una de ellas.
- Si todos los balances son cero, el resultado sigue siendo válido y `transfers` queda vacío.
- Los datos no se deduplican, corrigen ni completan automáticamente.

## Privacidad, accesibilidad y operación

La v1 no requiere secretos. Los nombres, descripciones e importes se tratan como datos introducidos por la persona usuaria: no se registrarán, enviarán ni almacenarán fuera de la ejecución. Las futuras pruebas, fixtures y demostraciones utilizarán solo datos sintéticos.

La CLI futura usará JSON UTF-8 y ayuda de texto plano; no dependerá de color, interacción, animación, emojis ni secuencias de control. La separación entre salida estándar, salida de error y código de proceso permite automatización, redirección y lectores de pantalla.

## Fuera de alcance de v1

- Persistencia, edición, historial, grupos, importación o exportación de datos.
- Múltiples monedas, conversión de divisas, impuestos, propinas, descuentos o presupuestos.
- Repartos ponderados, porcentajes, acciones, importes personalizados por participante o reglas por gasto distintas del reparto igualitario.
- Optimización global de la cantidad mínima de transferencias.
- Pagos reales, enlaces de cobro, cuentas, autenticación, autorización, red, API HTTP o interfaz gráfica.
- Lectura de entrada estándar, múltiples archivos, carga automática de archivos, configuración por variables de entorno o secretos.

## Criterios de aceptación de Fase 1

- La interfaz local, gramática de entrada, moneda, unidades menores, reparto igualitario, tratamiento de restos, balances y transferencias están cerrados.
- Cada entrada válida o inválida del catálogo [ESCENARIOS_FASE_1.md](ESCENARIOS_FASE_1.md) tiene resultado o diagnóstico inequívoco.
- La representación monetaria evita aritmética de coma flotante y el orden para distribuir restos es explícito.
- Las salidas, canales y códigos de proceso están definidos sin requerir una implementación existente.
- Persistencia, integraciones y extensiones de reparto se mantienen fuera de la primera versión.
