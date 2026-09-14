# Contrato v1 — Validador de configuración

## Estado y autoridad

Este documento es la fuente de verdad pública de la versión 1. Cierra las decisiones de la Fase 1 de [ROADMAP.md](../ROADMAP.md) y prevalece sobre descripciones de implementación posteriores. La Fase 2 preparó el entorno npm y sus dependencias; aún no existe código de validación, fixture funcional ni prueba automatizada de comportamiento.

- **Versión de contrato:** `v1`.
- **Interfaz prevista:** CLI local `env-config-validator`.
- **Entradas:** una ruta explícita de archivo `.env` y una ruta explícita de esquema JSON.
- **Salida correcta:** un único documento JSON UTF-8 por salida estándar.
- **Salida de error:** un único documento JSON UTF-8 por salida de error.
- **Estado:** sin red, persistencia, telemetría, cuentas ni consulta implícita de `process.env`.
- **Compatibilidad:** cambios incompatibles en argumentos, versión de esquema, reglas, envolturas o códigos de salida requerirán una versión posterior de contrato.

## Propósito, garantías y límites

La herramienta futura validará valores de un único archivo `.env` indicado por la persona usuaria contra un único esquema JSON `v1`. Su objetivo es detectar configuración ausente, mal formada, incompatible con el tipo declarado o contradictoria con otras claves.

Una validación correcta garantiza únicamente que el contenido explícitamente proporcionado satisface las reglas declaradas de este contrato. No certifica que las credenciales funcionen, que una URL sea accesible, que un host sea seguro, que un secreto sea válido, que una configuración sea adecuada para producción ni que una aplicación consumidora interprete los valores de la misma manera.

La v1 no carga, mezcla, modifica ni exporta `process.env`; no busca `.env` automáticamente; no implementa precedencia entre fuentes; no escribe archivos; no interpola `${VARIABLE}`; no expande shell; no ejecuta comandos; no acepta expresiones JavaScript; no carga módulos; no incorpora plugins; no soporta JSON Schema general, YAML, TOML, objetos anidados, API HTTP ni interfaz interactiva.

## Interfaz de línea de comandos

La interfaz futura admite exclusivamente estas formas:

```text
env-config-validator <ruta-env> <ruta-schema>
env-config-validator --help
env-config-validator -h
```

| Invocación                                                           | Salida estándar      | Salida de error             | Código |
| -------------------------------------------------------------------- | -------------------- | --------------------------- | :----: |
| Dos rutas válidas y configuración aceptada                           | Resumen JSON         | Vacía                       |  `0`   |
| `--help` o `-h` aislado                                              | Ayuda de texto plano | Vacía                       |  `0`   |
| Sin rutas, una ruta, más de dos argumentos o combinación de ayuda    | Vacía                | Error JSON de uso           |  `2`   |
| Opción no reconocida                                                 | Vacía                | Error JSON de uso           |  `2`   |
| Archivo no accesible, no regular, no UTF-8 o `.env` no interpretable | Vacía                | Error JSON de entrada       |  `3`   |
| JSON del esquema no interpretable                                    | Vacía                | Error JSON de esquema       |  `4`   |
| Esquema interpretable pero incompatible con este contrato            | Vacía                | Error JSON de esquema       |  `4`   |
| Esquema válido y configuración que incumple reglas                   | Vacía                | Error JSON de configuración |  `5`   |
| Fallo inesperado controlable                                         | Vacía                | Error JSON interno seguro   |  `1`   |

Las rutas se interpretarán exactamente como argumentos recibidos del intérprete de comandos. La herramienta no asumirá directorio de trabajo, no resolverá rutas fuera de la operación solicitada y no incluirá valores de configuración, contenido de archivos ni trazas en un diagnóstico público.

La ayuda estable será:

```text
Uso: env-config-validator <ruta-env> <ruta-schema>

Valida un archivo .env explícito contra un esquema JSON v1.
Ejemplo: env-config-validator ./config/demo.env ./config/schema.json
```

## Codificación y archivos de entrada

Los dos archivos se leerán como texto **UTF-8 sin BOM obligatorio**. Una implementación podrá aceptar BOM UTF-8 y deberá eliminarlo antes del análisis; cualquier otra codificación o secuencia no válida es un error `E_INPUT_NOT_UTF8`.

### Archivo `.env`

La Fase 2 seleccionó `dotenv` `16.4.7` como biblioteca mantenida de análisis. La futura Fase 5 deberá encapsularla y cumplir estas reglas observables de v1; no podrá ampliar su semántica sin actualizar el contrato:

- Una asignación tiene la forma `NOMBRE=valor`, con `NOMBRE` coincidente con `^[A-Za-z_][A-Za-z0-9_]*$`.
- Se permiten líneas vacías y comentarios cuyo primer carácter no blanco sea `#`.
- Se permite espacio blanco alrededor de `NOMBRE` y `=`; no forma parte de la clave.
- Los valores sin comillas se recortan de sus extremos; los valores entre comillas simples o dobles conservan el contenido interno según la semántica documentada por el parser elegido.
- Se permiten valores vacíos: `CLAVE=` representa una clave **presente** cuyo valor bruto es la cadena vacía.
- Una clave ausente es distinta de una clave presente con valor vacío.
- En caso de claves repetidas, la última asignación del archivo prevalece; la futura implementación no emitirá una advertencia por ello en v1.
- `export CLAVE=valor`, interpolación de variables, expansión de `$NOMBRE`, sustitución de comandos y evaluación de shell no forman parte de v1. Si el parser elegido aceptase alguna de estas extensiones, la implementación deberá rechazarlas o impedir que introduzcan semántica adicional.

Una línea que no pueda tratarse como comentario, línea vacía o asignación conforme a estas reglas provoca `E_INPUT_ENV_PARSE`; no se realiza validación parcial.

### Archivo de esquema

El esquema es JSON estricto y su documento raíz debe cumplir exactamente el formato de la sección siguiente. Comentarios, comas finales, referencias externas, claves duplicadas con semántica dependiente del parser y cualquier formato distinto de JSON son inválidos. El documento se considera inválido con `E_SCHEMA_JSON_PARSE` si no puede interpretarse como JSON y con `E_SCHEMA_INVALID` si su estructura o semántica no cumple el contrato.

## Formato de esquema JSON v1

El documento raíz debe ser un objeto con estas claves y ninguna otra:

| Clave          | Tipo   | Obligatoria | Regla                                                              |
| -------------- | ------ | :---------: | ------------------------------------------------------------------ |
| `version`      | cadena |     Sí      | Debe ser exactamente `"v1"`.                                       |
| `variables`    | objeto |     Sí      | Mapa no vacío de nombre de variable a regla declarativa.           |
| `unknownKeys`  | cadena |     No      | `"allow"`, `"warn"` o `"error"`; valor por defecto: `"warn"`.      |
| `dependencies` | lista  |     No      | Lista de reglas globales de dependencia; por defecto: lista vacía. |

Los nombres de las propiedades de `variables` deben cumplir `^[A-Za-z_][A-Za-z0-9_]*$`. Las claves se comparan exactamente, con sensibilidad a mayúsculas y minúsculas.

Ejemplo exclusivamente documental y con datos ficticios:

```json
{
  "version": "v1",
  "unknownKeys": "warn",
  "variables": {
    "APP_PORT": {
      "type": "number",
      "required": true,
      "integer": true,
      "min": 1,
      "max": 65535,
      "transforms": ["trim"]
    },
    "API_TOKEN": {
      "type": "string",
      "required": true,
      "secret": true,
      "minLength": 12
    }
  },
  "dependencies": [
    {
      "kind": "requires",
      "if": "API_TOKEN",
      "then": "APP_PORT"
    }
  ]
}
```

El ejemplo ilustra sintaxis, no proporciona una credencial ni autoriza a mostrar valores secretos en una salida futura.

## Reglas de variable

Cada valor del mapa `variables` es un objeto. Solo se admiten las claves indicadas en esta sección y en la tabla específica del tipo; cualquier clave adicional invalida el esquema con `E_SCHEMA_UNKNOWN_FIELD`.

### Campos comunes

| Campo         | Tipo             | Predeterminado | Regla                                                                                                       |
| ------------- | ---------------- | -------------- | ----------------------------------------------------------------------------------------------------------- |
| `type`        | cadena           | —              | Obligatorio: `string`, `number`, `boolean`, `enum`, `url` o `list`.                                         |
| `required`    | booleano         | `false`        | Si es `true`, la clave debe estar presente o disponer de `default`.                                         |
| `secret`      | booleano         | `false`        | Controla redacción de valores; no cambia la validación.                                                     |
| `default`     | valor JSON       | Ausente        | Debe ser compatible con el tipo y con todas sus restricciones después del mismo pipeline de transformación. |
| `transforms`  | lista de cadenas | `[]`           | Lista ordenada de transformaciones seguras admitidas.                                                       |
| `description` | cadena           | Ausente        | Texto opcional de documentación; no se incluirá por defecto en resultados ni errores.                       |

Una variable no requerida y ausente se considera **no proporcionada**: no se transforma, no se convierte, no genera una incidencia de tipo y no cuenta como presente para dependencias. Una variable con `default` se considera presente para la validación y para dependencias; su resumen público indicará que procede de un valor por defecto sin revelar el valor.

Un valor vacío (`CLAVE=`) está presente. Salvo una transformación que lo modifique, se valida como cadena vacía; no activa `default` y no equivale a ausencia.

### Tipos y restricciones

| `type`    | Entrada final válida               | Campos adicionales permitidos       |
| --------- | ---------------------------------- | ----------------------------------- |
| `string`  | Cadena UTF-8                       | `minLength`, `maxLength`, `pattern` |
| `number`  | Número decimal finito              | `integer`, `min`, `max`             |
| `boolean` | Booleano                           | Ninguno                             |
| `enum`    | Una de las cadenas declaradas      | `values`                            |
| `url`     | URL absoluta `http:` o `https:`    | `protocols`                         |
| `list`    | Lista JSON de escalares homogéneos | `items`, `minItems`, `maxItems`     |

Las restricciones que no correspondan al tipo invalidan el esquema. Por ejemplo, `pattern` en una variable `number`, `min` en `string`, `integer` en `boolean` o `items` fuera de `list` son errores de esquema, no errores de configuración.

#### `string`

- `minLength` y `maxLength` son enteros no negativos.
- Si ambos existen, `minLength` no puede superar `maxLength`.
- La longitud se mide en unidades de código UTF-16 de JavaScript, que será la referencia de implementación v1.
- `pattern`, cuando existe, es un objeto con `source` y `flags`.
- `source` debe ser una cadena no vacía de 1 a 256 unidades de código.
- `flags` es opcional y solo puede contener, sin repetición, `i`, `m` y `u`.
- El patrón se compila al validar el esquema. Si no puede construirse como `RegExp`, el esquema es inválido con `E_SCHEMA_INVALID_PATTERN`.
- La v1 no acepta flags `g`, `y`, `s`, `d` ni cadenas RegExp literales.

Los patrones son expresiones regulares aportadas por la persona usuaria. No ejecutan código, pero pueden tener coste de cálculo. V1 limita la longitud y flags, no promete inmunidad total frente a expresiones de coste elevado y no es adecuada para entradas no confiables de tamaño ilimitado.

#### `number`

- El valor transformado debe representar un decimal finito completo según `Number(valor)` y no puede ser una cadena vacía.
- No se admiten `NaN`, `Infinity`, `-Infinity`, hexadecimal, binario ni separadores numéricos.
- `integer`, si existe, debe ser booleano y exige un entero seguro de JavaScript.
- `min` y `max`, si existen, deben ser números JSON finitos; `min` no puede superar `max`.
- Los límites son inclusivos.

#### `boolean`

Tras las transformaciones permitidas, se aceptan exactamente las cadenas ASCII `true` y `false`, en minúsculas. No se aceptan `1`, `0`, `yes`, `no`, mayúsculas ni variantes localizadas salvo que una transformación `lowercase` se haya declarado explícitamente antes de la conversión.

#### `enum`

- `values` es obligatorio y contiene entre 1 y 100 cadenas no vacías, todas distintas por comparación exacta.
- El valor final debe coincidir exactamente con una entrada de `values`.
- Las transformaciones pueden cambiar el valor antes de la comparación.

#### `url`

- La URL debe ser absoluta y construible por la API `URL` estándar de JavaScript.
- Solo se permiten los protocolos `http:` y `https:` salvo que `protocols` declare una lista no vacía de protocolos permitidos.
- Cada protocolo de `protocols` es una cadena en minúsculas con el sufijo `:`, de la forma `^[a-z][a-z0-9+.-]*:$`.
- No se comprueba resolución DNS, conectividad, certificados, reputación ni seguridad del destino.

#### `list`

- El valor final debe ser texto JSON que represente un array o la representación interna de una lista de cadenas producida por `splitComma`.
- `items` es obligatorio y debe ser uno de `string`, `number` o `boolean`.
- Todos los elementos deben ser del tipo declarado; no se permiten arrays, objetos, `null` ni mezcla de tipos.
- Para `number`, los elementos deben ser números JSON finitos; para `boolean`, booleanos JSON; para `string`, cadenas JSON.
- `minItems` y `maxItems`, si existen, son enteros no negativos; `minItems` no puede superar `maxItems`.
- Los límites incluyen elementos repetidos; la v1 no impone unicidad ni restricciones por elemento adicionales.

## Transformaciones seguras

`transforms` se aplica en el orden exacto de la lista **solo a valores de texto presentes**, incluidos los valores `default` que sean cadenas. Después se realiza la conversión al tipo y luego se aplican sus restricciones. Las transformaciones disponibles son cerradas:

| Transformación | Entrada    | Resultado                                                           | Restricción                                            |
| -------------- | ---------- | ------------------------------------------------------------------- | ------------------------------------------------------ |
| `trim`         | Texto      | Elimina espacios Unicode de ambos extremos.                         | Puede aparecer una vez.                                |
| `lowercase`    | Texto      | `toLowerCase()` de JavaScript.                                      | Puede aparecer una vez.                                |
| `uppercase`    | Texto      | `toUpperCase()` de JavaScript.                                      | Puede aparecer una vez.                                |
| `splitComma`   | Texto      | Representación interna de una lista de cadenas separadas por comas. | Solo para `list`; no puede combinarse con `parseJson`. |
| `parseJson`    | Texto JSON | Conserva el texto para conversión JSON del tipo `list`.             | Solo para `list`; puede aparecer como máximo una vez.  |

`splitComma` divide por coma ASCII, aplica `trim` Unicode a cada segmento y produce una representación interna de lista de cadenas que la conversión de `list` consume directamente; no serializa ni vuelve a interpretar JSON. Las comas escapadas, CSV, comillas CSV y separadores configurables no forman parte de v1. Una cadena vacía produce una lista con un único elemento vacío.

`parseJson` no evalúa código: solo delega el texto a `JSON.parse` durante la conversión de un `list`. Para `list`, la ausencia de `parseJson` sigue usando el mismo análisis JSON normativo; la transformación existe para declarar intención y no altera el resultado. Por tanto, `parseJson` es redundante pero válido; no deberá utilizarse como mecanismo para parsear tipos que no sean `list`.

No se admiten nombres de transformación no listados, parámetros, expresiones, plantillas, referencias a otras variables, comandos, imports, funciones ni rutas de módulos. Una lista con transformaciones incompatibles, repetidas cuando se prohíben o aplicadas a un tipo incorrecto invalida el esquema.

## Pipeline normativo de cada variable

La implementación futura deberá seguir este orden sin reordenarlo:

1. Localizar la clave en el mapa parseado del archivo `.env`.
2. Si la clave está ausente y existe `default`, usar el valor por defecto y marcar origen `default`.
3. Si sigue ausente y `required` es `true`, emitir `E_CONFIG_REQUIRED`.
4. Si sigue ausente y no es obligatoria, marcarla como no proporcionada y no continuar.
5. Si el valor procede del `.env`, tratarlo como texto, incluso si está vacío.
6. Si el valor por defecto no es texto, saltar transformaciones y usarlo como valor de tipo JSON; si es texto, aplicar transformaciones.
7. Aplicar transformaciones declaradas de izquierda a derecha.
8. Convertir el resultado al tipo declarado; para `list`, esta conversión acepta texto JSON o la representación interna creada por `splitComma`.
9. Aplicar restricciones específicas del tipo.
10. Registrar un estado seguro de la variable, sin incluir su valor cuando `secret` es `true`.
11. Después de procesar todas las variables, evaluar las dependencias sobre las claves consideradas presentes y válidas.
12. Ordenar incidencias por clave, luego por código y, por último, por la posición declarada de la regla; esta ordenación es parte de la salida determinista.

Un fallo de conversión o restricción no detiene la evaluación de las demás variables. La salida de configuración inválida contiene todas las incidencias determinables sin revelar valores.

## Claves no declaradas

Una clave presente en el archivo `.env` que no exista en `variables` se trata según `unknownKeys`:

| Política | Efecto                                                             |
| -------- | ------------------------------------------------------------------ |
| `allow`  | Se ignora; no se muestra en el resumen.                            |
| `warn`   | No invalida; genera una advertencia segura `W_CONFIG_UNKNOWN_KEY`. |
| `error`  | Invalida; genera `E_CONFIG_UNKNOWN_KEY`.                           |

La clave puede aparecer en una advertencia o incidencia porque el nombre no es un valor secreto. El valor asociado jamás se incluye, incluso si la clave no está declarada.

## Dependencias globales

Cada regla en `dependencies` es exactamente una de las siguientes formas:

```json
{ "kind": "allOrNone", "keys": ["A", "B"] }
{ "kind": "requires", "if": "A", "then": "B" }
{ "kind": "forbids", "if": "A", "then": "B" }
```

- Todos los nombres referenciados deben existir en `variables`; de lo contrario, el esquema es inválido con `E_SCHEMA_UNKNOWN_REFERENCE`.
- `allOrNone.keys` contiene entre 2 y 50 nombres distintos.
- `requires` y `forbids` requieren dos nombres distintos.
- Una clave cuenta como presente para dependencia solo si está presente en el `.env` o se resolvió mediante `default`, y además superó conversión y restricciones.
- `allOrNone` se incumple cuando al menos una clave del grupo está presente y válida, pero no todas lo están presentes y válidas. Se genera una incidencia `E_CONFIG_ALL_OR_NONE` por regla, asociada a la lista ordenada de claves.
- `requires` se incumple cuando `if` está presente y válida y `then` no está presente y válida. Se genera `E_CONFIG_REQUIRES` asociado a `if`.
- `forbids` se incumple cuando ambas claves están presentes y válidas. Se genera `E_CONFIG_FORBIDS` asociado a `if`.
- Las reglas no transforman datos ni crean valores. Pueden coexistir, y cada una que se incumpla genera su propia incidencia.
- Un esquema no puede contener dos reglas idénticas por comparación estructural. Una duplicación es `E_SCHEMA_DUPLICATE_DEPENDENCY`.

## Envoltorios JSON públicos

### Resumen correcto

Si no existe incidencia de severidad `error`, la herramienta devuelve exactamente una envoltura de esta forma conceptual:

```json
{
  "valid": true,
  "schemaVersion": "v1",
  "summary": {
    "declared": 2,
    "provided": 2,
    "defaulted": 0,
    "warnings": 1
  },
  "variables": [
    {
      "key": "APP_PORT",
      "status": "valid",
      "source": "env",
      "secret": false
    },
    {
      "key": "API_TOKEN",
      "status": "valid",
      "source": "env",
      "secret": true
    }
  ],
  "warnings": [
    {
      "code": "W_CONFIG_UNKNOWN_KEY",
      "key": "LEGACY_FLAG",
      "message": "La clave no está declarada en el esquema."
    }
  ]
}
```

- `variables` se ordena ascendentemente por `key`.
- `provided` cuenta claves declaradas presentes y válidas, incluidas las de origen `default`.
- `defaulted` cuenta las de origen `default`.
- `warnings` cuenta advertencias de la lista homónima.
- Una variable no proporcionada y opcional se representa con `status: "absent"` y `source: "none"`.
- Una variable declarada `secret: true` se representa igual que cualquier otra, pero nunca incluye `value`, valor transformado, longitud, patrón evaluado, valor por defecto ni representación derivada.
- La v1 tampoco expone valores de variables no secretas; el resumen comunica estado y origen, no datos de configuración.

### Error público

Todo fallo se serializa como:

```json
{
  "error": {
    "code": "E_CONFIG_REQUIRED",
    "category": "configuration",
    "message": "La configuración no cumple el esquema.",
    "issues": [
      {
        "code": "E_CONFIG_REQUIRED",
        "key": "API_TOKEN",
        "rule": "required",
        "message": "Falta una variable obligatoria."
      }
    ]
  }
}
```

`issues` es una lista, posiblemente vacía solo para fallos de uso, entrada o error interno. Las incidencias no incluirán valores recibidos, valores transformados, valores por defecto, fragmentos de archivos, rutas absolutas, trazas, credenciales, tokens ni datos derivados de secretos.

| Categoría       | Códigos posibles                                                                                                                                               | Mensaje principal estable                    |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| `usage`         | `E_USAGE_ARGUMENTS`, `E_USAGE_UNKNOWN_OPTION`                                                                                                                  | `La invocación no cumple el uso esperado.`   |
| `input`         | `E_INPUT_READ`, `E_INPUT_NOT_UTF8`, `E_INPUT_ENV_PARSE`                                                                                                        | `No se pudo preparar un archivo de entrada.` |
| `schema`        | `E_SCHEMA_JSON_PARSE`, `E_SCHEMA_INVALID`, `E_SCHEMA_UNKNOWN_FIELD`, `E_SCHEMA_UNKNOWN_REFERENCE`, `E_SCHEMA_INVALID_PATTERN`, `E_SCHEMA_DUPLICATE_DEPENDENCY` | `El esquema no cumple el contrato v1.`       |
| `configuration` | `E_CONFIG_REQUIRED`, `E_CONFIG_UNKNOWN_KEY`, `E_CONFIG_TYPE`, `E_CONFIG_CONSTRAINT`, `E_CONFIG_ALL_OR_NONE`, `E_CONFIG_REQUIRES`, `E_CONFIG_FORBIDS`           | `La configuración no cumple el esquema.`     |
| `internal`      | `E_INTERNAL`                                                                                                                                                   | `No se pudo completar la validación.`        |

Los mensajes de las incidencias son estables, genéricos y no incluyen contenido de valores. Los `rule` previstos son `required`, `unknownKey`, `type`, `constraint`, `allOrNone`, `requires` y `forbids`.

## Modelo de secretos

El campo `secret: true` es una garantía de presentación, no de cifrado ni de gestión de secretos. Su efecto obligatorio es:

- No incluir valor bruto, valor transformado, valor convertido, valor por defecto, longitud, hash, prefijo, sufijo, patrón, representación serializada ni mensaje derivado en stdout, stderr, logs, tests, snapshots, fixtures documentales o activos de demostración.
- Permitir solo el nombre, estado, origen y el booleano `secret` en el resumen público.
- Para una incidencia de secreto, usar el mismo mensaje genérico de regla que para cualquier clave, sin reflejar el valor.
- Tratar los valores de claves desconocidas como sensibles por defecto: sus valores tampoco se muestran.

La responsabilidad de no versionar archivos reales permanece en quien usa la herramienta. Un esquema no debe contener un secreto real en `default`; aunque una implementación lo redactaría, almacenar ese dato en el esquema ya sería una exposición fuera de la protección de la CLI.

## Accesibilidad y operación

La CLI usará texto JSON UTF-8 y ayuda de texto plano. No dependerá de color, interacción, animación, emojis ni secuencias de control. La separación entre stdout, stderr y código de proceso permite automatización, redirección y lectores de pantalla. La herramienta futura funcionará enteramente de forma local y no requerirá credenciales propias.

## Criterios de aceptación de Fase 1

- Quedan cerrados argumentos, entradas UTF-8, semántica de `.env`, versión y gramática del esquema, tipos, transformaciones, dependencias, envolturas, mensajes principales y códigos de salida.
- Cada condición de error posee una categoría, identificador y salida pública inequívoca.
- La diferencia entre ausencia, vacío y valor por defecto está definida.
- Las transformaciones son declarativas, cerradas y no pueden ejecutar código o acceder a recursos.
- El modelo de secretos prohíbe explícitamente la exposición de valores o derivados en cualquier salida pública.
- Los escenarios de [ESCENARIOS_FASE_1.md](ESCENARIOS_FASE_1.md) disponen de un resultado o diagnóstico único.
- La implementación, los fixtures ejecutables y las pruebas automatizadas siguen pendientes de fases posteriores; el entorno y las dependencias aisladas se prepararon en la Fase 2.

## Decisiones aplazadas

- Admisión de fuentes adicionales, capas de precedencia o integración controlada con `process.env`.
- Variables anidadas, JSON Schema, otros formatos de esquema o formatos de salida alternativos.
- Operadores de dependencia adicionales, por ejemplo `atLeastOne` o condiciones por valor.
- Restricciones por elemento de listas, tipos de lista complejos, unicidad y separación configurable.
- Mitigación completa de expresiones regulares de alto coste, evaluación temporal o límites configurables de tamaño de archivo.
- Escritura de configuraciones normalizadas, reparación automática, cifrado, gestores de secretos, servicios cloud, API o interfaz gráfica.
