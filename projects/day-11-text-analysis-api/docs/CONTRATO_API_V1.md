# Contrato API v1 — Análisis de texto

## Estado y compatibilidad

Este documento es la fuente de verdad pública de la versión 1. Define el comportamiento implementado de la API y prevalece sobre sus detalles internos.

- **Versión de contrato:** v1.
- **Formato:** JSON UTF-8.
- **Ruta pública:** `POST /api/v1/analyze`.
- **Compatibilidad:** un cambio incompatible requerirá una nueva versión de contrato; añadir campos opcionales de respuesta no será incompatible.
- **Sin estado:** cada solicitud se analiza de forma independiente. La API no conserva el texto ni el resultado.

## Operación

| Campo | Valor |
|---|---|
| Método | `POST` |
| Ruta | `/api/v1/analyze` |
| Tipo de contenido admitido | `application/json` |
| Tipo de respuesta correcta | `application/json; charset=utf-8` |
| Autenticación | No requerida en v1 |

Solo se define esta operación en v1. No existen rutas de persistencia, consulta de historial ni carga de archivos.

## Solicitud correcta

El cuerpo JSON debe contener **exactamente** la propiedad `text`.

```json
{
  "text": "La API analiza texto. La API devuelve métricas útiles."
}
```

### Campo `text`

| Regla | Valor |
|---|---|
| Tipo | Cadena JSON |
| Obligatorio | Sí |
| Longitud mínima | 1 carácter Unicode |
| Longitud máxima | 10.000 caracteres Unicode |
| Espacios | Se conservan para los conteos de caracteres y la segmentación; no se recortan antes del análisis |
| Campos adicionales | No permitidos |

Una cadena formada únicamente por espacios, tabulaciones o saltos de línea es válida: sus métricas lingüísticas serán cero. Una cadena vacía no es válida.

## Respuesta correcta

Una solicitud válida devolverá `200 OK` con la siguiente forma:

```json
{
  "metrics": {
    "character_count": 54,
    "character_count_without_whitespace": 46,
    "word_count": 9,
    "sentence_count": 2,
    "paragraph_count": 1,
    "estimated_reading_time_seconds": 3
  },
  "word_frequencies": [
    {"word": "api", "count": 2},
    {"word": "la", "count": 2},
    {"word": "analiza", "count": 1},
    {"word": "devuelve", "count": 1},
    {"word": "métricas", "count": 1},
    {"word": "texto", "count": 1},
    {"word": "útiles", "count": 1}
  ],
  "keywords": [
    {"word": "api", "count": 2},
    {"word": "analiza", "count": 1},
    {"word": "devuelve", "count": 1},
    {"word": "métricas", "count": 1},
    {"word": "texto", "count": 1}
  ]
}
```

Los valores del ejemplo están versionados como referencia reproducible en [`data/expected/contract-example.json`](../data/expected/contract-example.json) y se verifican contra el fixture [`data/fixtures/contract-example.txt`](../data/fixtures/contract-example.txt) mediante la suite automatizada.

### Propiedad `metrics`

| Campo | Tipo | Definición |
|---|---|---|
| `character_count` | entero no negativo | Número de caracteres Unicode del valor recibido en `text`, incluidos espacios y saltos de línea. |
| `character_count_without_whitespace` | entero no negativo | Número de caracteres de `text` que no cumplen la clasificación Unicode de espacio en blanco. |
| `word_count` | entero no negativo | Número de tokens de palabra definidos en la sección de tokenización. |
| `sentence_count` | entero no negativo | Número de segmentos de frase no vacíos definidos en la sección de frases. |
| `paragraph_count` | entero no negativo | Número de párrafos no vacíos definidos en la sección de párrafos. |
| `estimated_reading_time_seconds` | entero no negativo | Tiempo de lectura estimado con redondeo hacia arriba a partir de `word_count`. |

El tiempo estimado usa una velocidad fija de **200 palabras por minuto**: `ceil(word_count / 200 × 60)`. Con cero palabras, el valor es `0`.

### Propiedad `word_frequencies`

Es una lista completa de palabras normalizadas. Cada elemento contiene:

| Campo | Tipo | Regla |
|---|---|---|
| `word` | cadena | Token normalizado según las reglas de esta versión. |
| `count` | entero positivo | Número de apariciones del token normalizado. |

La lista se ordena primero por `count` descendente y, en caso de empate, por `word` en orden lexicográfico ascendente de puntos de código Unicode. No tiene límite de elementos en v1.

### Propiedad `keywords`

Es una lista de **hasta cinco** elementos con la misma forma que `word_frequencies`. Se obtiene a partir de las frecuencias de palabras tras excluir las palabras vacías definidas a continuación.

Las palabras vacías de v1 son, tras normalización: `a`, `al`, `and`, `de`, `del`, `el`, `en`, `es`, `for`, `in`, `la`, `las`, `los`, `of`, `or`, `para`, `por`, `the`, `to`, `un`, `una`, `y`.

Las palabras restantes se ordenan con la misma regla de frecuencia y desempate que `word_frequencies`; se devuelven las primeras cinco. Si no hay candidatas, la lista es vacía.

## Reglas deterministas de análisis

### Unicode y normalización

1. El texto de entrada se conserva sin modificar para `character_count`, `character_count_without_whitespace`, frases y párrafos.
2. Para identificar palabras, se aplica normalización Unicode NFC y después conversión a minúsculas Unicode.
3. No se eliminan tildes, diacríticos ni letras no ASCII. Por ejemplo, `canción` y `cancion` son palabras distintas.
4. La comparación de frecuencias y palabras vacías usa el token normalizado.

### Palabras y puntuación

1. Una palabra es una secuencia máxima de letras Unicode o dígitos Unicode.
2. Los apóstrofes, guiones, guiones bajos, emojis y cualquier signo de puntuación son separadores; no forman parte de una palabra.
3. Los números son palabras válidas y participan en `word_count` y `word_frequencies`.
4. Los tokens vacíos nunca se incluyen.

Ejemplos documentales:

| Entrada | Palabras normalizadas |
|---|---|
| `Hola, MUNDO!` | `hola`, `mundo` |
| `re-usable_test` | `re`, `usable`, `test` |
| `C# y 2026` | `c`, `y`, `2026` |
| `canción cancion` | `canción`, `cancion` |

### Frases

1. Los delimitadores de frase son `.`, `!`, `?`, `…` y los saltos de línea `\n` o `\r\n`.
2. Una secuencia de uno o más delimitadores consecutivos cierra una única frase.
3. Solo se cuenta un segmento que contenga al menos una palabra según la definición anterior.
4. El texto final con palabras y sin delimitador terminal cuenta como una frase.
5. La puntuación o los espacios sin palabras no crean frases.

### Párrafos

1. Un párrafo es una secuencia de una o más líneas no vacías, separada de otras por una o más líneas vacías.
2. Una línea vacía es aquella que contiene únicamente caracteres Unicode de espacio en blanco.
3. Solo se cuenta un párrafo que contenga al menos una palabra.
4. Los saltos de línea simples dentro de un bloque no separan párrafos.

## Respuestas de error

Todos los errores tienen `application/json; charset=utf-8` y la forma:

```json
{
  "error": {
    "code": "validation_error",
    "message": "La solicitud no cumple el contrato.",
    "details": [
      {
        "field": "text",
        "rule": "min_length",
        "message": "text debe contener al menos 1 carácter."
      }
    ]
  }
}
```

`details` es una lista que puede estar vacía cuando no se pueda asociar el error a un campo concreto. Cada elemento contiene `field`, `rule` y `message` como cadenas.

| Estado | Código | Cuándo se usa |
|---:|---|---|
| 400 | `invalid_json` | El cuerpo no puede interpretarse como JSON. |
| 415 | `unsupported_media_type` | La solicitud no usa `application/json`. |
| 422 | `validation_error` | Falta `text`, su tipo no es cadena, está vacío, supera 10.000 caracteres o existen campos no permitidos. |
| 405 | `method_not_allowed` | Se usa un método distinto de `POST` sobre la ruta. |
| 500 | `internal_error` | Fallo inesperado no atribuible al cliente; no debe exponer detalles internos. |

Para errores de validación, `field` será `text` cuando la infracción corresponda a esa propiedad, `body` cuando afecte al cuerpo completo, o el nombre del campo adicional rechazado cuando corresponda.

## Ejemplos documentales adicionales

### Texto compuesto solo por espacios

**Solicitud:**

```json
{
  "text": " \t\n "
}
```

**Respuesta esperada:** `200 OK`; todos los conteos lingüísticos, las frecuencias y las palabras clave son cero o listas vacías. `character_count` conserva el número de caracteres recibido y `character_count_without_whitespace` es `0`.

### Cadena vacía

**Solicitud:**

```json
{
  "text": ""
}
```

**Respuesta esperada:** `422 Unprocessable Entity` con `error.code` igual a `validation_error` y un detalle para `text` con regla `min_length`.

### Propiedad desconocida

**Solicitud:**

```json
{
  "text": "texto válido",
  "language": "es"
}
```

**Respuesta esperada:** `422 Unprocessable Entity` con `error.code` igual a `validation_error` y un detalle que identifique `language` como campo no permitido.

## Límites y no objetivos

- El límite de 10.000 caracteres se aplica a una sola solicitud y no establece rate limiting.
- La selección de palabras clave no pretende inferir significado, idioma ni relevancia semántica.
- La lista de palabras vacías es fija y limitada a v1; no existe detección ni configuración de idioma.
- No se almacena ningún texto, resultado o dato de solicitud.
- Este contrato no define autenticación, base de datos, servicios externos, carga de archivos ni despliegue.