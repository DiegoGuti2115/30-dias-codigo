# Contrato v1 — Generador de slugs

## Propósito

Este contrato cierra el comportamiento de la primera versión antes de crear entorno TypeScript, implementación, pruebas ejecutables o configuración funcional. La utilidad futura transforma **un único texto** en un slug ASCII determinista y comunica los errores de uso o contenido mediante una CLI local, sin estado ni dependencias de red.

## Principios y límites

- Una operación transforma una única cadena de texto suministrada como argumento posicional.
- Un resultado correcto contiene exclusivamente letras ASCII minúsculas, dígitos ASCII y guiones ASCII simples.
- La operación no lee archivos, entrada estándar, variables de entorno ni configuración; tampoco escribe archivos, persiste datos ni realiza red.
- La herramienta no resuelve colisiones ni añade sufijos implícitos.
- La versión 1 no translitera exhaustivamente alfabetos no latinos ni conserva Unicode en el resultado.
- No existen opciones configurables, subcomandos, modo interactivo, procesamiento por lotes ni API HTTP.
- La futura implementación separará la transformación pura del adaptador de terminal; este contrato define ambos comportamientos, sin prescribir módulos ni bibliotecas.

## Dominio de entrada del núcleo futuro

La transformación interna futura admite exclusivamente un valor de tipo cadena primitiva. No acepta objetos cadena, valores nulos, ausentes, números, booleanos, arreglos ni objetos.

Una cadena se rechaza antes de transformar si, después de retirar el espacio en blanco Unicode de sus extremos, está vacía. Una cadena no vacía puede transformarse y aun así ser rechazada si no deja ningún carácter permitido en el resultado.

| Condición                                   | Clasificación       | Identificador de diagnóstico futuro |
| ------------------------------------------- | ------------------- | ----------------------------------- |
| Valor ausente o argumento no proporcionado  | Error de uso en CLI | `E_USAGE_MISSING_TEXT`              |
| Más de un argumento posicional              | Error de uso en CLI | `E_USAGE_TOO_MANY_ARGUMENTS`        |
| Opción no reconocida                        | Error de uso en CLI | `E_USAGE_UNKNOWN_OPTION`            |
| Valor no textual para el núcleo             | Error de validación | `E_INPUT_NOT_TEXT`                  |
| Cadena vacía o solo de espacios Unicode     | Error de validación | `E_INPUT_EMPTY`                     |
| Cadena que no produce caracteres permitidos | Error de contenido  | `E_INPUT_NOT_NORMALIZABLE`          |

Los identificadores son estables para la implementación y las pruebas futuras; la CLI v1 mostrará los mensajes definidos más adelante, no los identificadores salvo que una fase posterior lo documente expresamente.

## Algoritmo de normalización v1

La futura implementación aplicará esta secuencia lógica, sin reordenarla:

1. **Validar el tipo y la presencia.** Rechazar cualquier valor que no sea una cadena primitiva y rechazar cadenas vacías tras el recorte definido en el paso siguiente.
2. **Recortar extremos.** Eliminar espacios en blanco Unicode al inicio y al final. El espacio incluye cualquier carácter reconocido como espacio en blanco por el mecanismo Unicode estándar elegido en la Fase 2.
3. **Descomponer Unicode.** Aplicar normalización canónica de compatibilidad `NFKD` a la cadena recortada.
4. **Eliminar marcas combinantes.** Descartar los caracteres cuya categoría Unicode sea una marca combinante. Esta regla elimina los diacríticos separables generados por `NFKD`.
5. **Convertir a minúsculas.** Aplicar conversión Unicode a minúsculas al texto restante.
6. **Clasificar carácter a carácter.** Conservar solo `a`–`z` y `0`–`9`. Cada grupo no vacío de caracteres no conservables situado entre dos grupos conservables representa una frontera pendiente.
7. **Emitir separadores.** Antes de emitir el siguiente carácter conservable, emitir un único guion si hay una frontera pendiente y ya existe contenido emitido. Los caracteres no conservables de borde no emiten guiones.
8. **Validar el resultado.** Si no se emitió ningún carácter conservable, rechazar la entrada con `E_INPUT_NOT_NORMALIZABLE`.

La salida correcta cumple de forma obligatoria el patrón `^[a-z0-9]+(?:-[a-z0-9]+)*$`.

### Acentos y caracteres latinos

La eliminación de diacríticos se basa en `NFKD` y categorías Unicode. Por tanto, los ejemplos siguientes están cerrados:

| Entrada        | Resultado      |
| -------------- | -------------- |
| `áéíóúüñç`     | `aeiouunc`     |
| `À bientôt`    | `a-bientot`    |
| `Crème brûlée` | `creme-brulee` |
| `niño`         | `nino`         |

Para los caracteres latinos que no se descomponen de manera útil con `NFKD`, la v1 adopta una tabla mínima y explícita aplicada **después** de la descomposición y antes del filtrado ASCII:

| Carácter original, mayúscula o minúscula | Sustitución |
| ---------------------------------------- | ----------- |
| `ß` / `ẞ`                                | `ss`        |
| `æ` / `Æ`                                | `ae`        |
| `œ` / `Œ`                                | `oe`        |
| `ø` / `Ø`                                | `o`         |
| `ð` / `Ð`                                | `d`         |
| `þ` / `Þ`                                | `th`        |
| `ł` / `Ł`                                | `l`         |
| `đ` / `Đ`                                | `d`         |
| `ı`                                      | `i`         |

La tabla es cerrada en v1. Todo carácter no ASCII que no quede transformado por `NFKD`, eliminación de marcas o esta tabla se trata como no conservable. No se añaden transliteraciones para chino, cirílico, árabe, japonés, coreano, emojis u otros alfabetos.

### Separadores, símbolos y puntuación

Los espacios Unicode, tabulaciones, saltos de línea, guiones de cualquier tipo, guiones bajos, barras, puntuación, símbolos, comillas, signos de control, emojis y caracteres Unicode no conservables se tratan uniformemente como no conservables.

- Un grupo de uno o más de esos caracteres entre contenido conservable se representa por un único guion.
- Un grupo al principio o al final se descarta.
- No se concatena contenido separado por símbolos: `c++ guía` produce `c-guia`.
- Un guion ASCII existente no se conserva por sí mismo; participa en la misma regla de frontera. Así se evita cualquier guion inicial, final o repetido.
- Los caracteres no latinos situados entre fragmentos ASCII también forman frontera. Por ejemplo, `uno中文dos` produce `uno-dos`.

## Interfaz de línea de comandos v1

La interfaz futura tendrá exclusivamente estas formas:

```text
slug-generator <texto>
slug-generator --help
slug-generator -h
```

| Invocación                                                  | Salida estándar                    | Salida de error                    | Código de salida |
| ----------------------------------------------------------- | ---------------------------------- | ---------------------------------- | :--------------: |
| `slug-generator <texto>` con texto válido                   | El slug y un único salto de línea. | Vacía.                             |       `0`        |
| `slug-generator --help` o `slug-generator -h`               | Texto de ayuda estable.            | Vacía.                             |       `0`        |
| Sin argumentos                                              | Vacía.                             | Mensaje de uso.                    |       `2`        |
| Dos o más argumentos posicionales                           | Vacía.                             | Mensaje de uso.                    |       `2`        |
| Cualquier opción distinta de `--help` o `-h`                | Vacía.                             | Mensaje de uso.                    |       `2`        |
| `--help` o `-h` combinada con cualquier argumento adicional | Vacía.                             | Mensaje de uso.                    |       `2`        |
| Texto vacío, solo espacios o no normalizable                | Vacía.                             | Mensaje de validación o contenido. |       `1`        |
| Fallo inesperado controlable                                | Vacía.                             | Mensaje breve sin traza.           |       `1`        |

La ayuda estable será exactamente:

```text
Uso: slug-generator <texto>

Convierte un único texto en un slug ASCII en minúsculas.
Ejemplo: slug-generator "Guía rápida de TypeScript"
```

Los mensajes estables de error serán exactamente:

| Identificador                | Mensaje                                                                                |
| ---------------------------- | -------------------------------------------------------------------------------------- |
| `E_USAGE_MISSING_TEXT`       | `Error: falta el argumento <texto>. Usa --help para consultar el uso.`                 |
| `E_USAGE_TOO_MANY_ARGUMENTS` | `Error: se admite exactamente un argumento <texto>. Usa --help para consultar el uso.` |
| `E_USAGE_UNKNOWN_OPTION`     | `Error: opción no reconocida. Usa --help para consultar el uso.`                       |
| `E_INPUT_EMPTY`              | `Error: el texto no puede estar vacío ni contener solo espacios.`                      |
| `E_INPUT_NOT_NORMALIZABLE`   | `Error: el texto no contiene caracteres que puedan formar un slug.`                    |
| `E_INPUT_NOT_TEXT`           | `Error: la entrada debe ser texto.`                                                    |
| Error inesperado             | `Error: no se pudo generar el slug.`                                                   |

La CLI recibe cadenas desde el proceso; por ello `E_INPUT_NOT_TEXT` corresponde al contrato del núcleo y no es un estado alcanzable mediante argumentos normales de terminal. Los mensajes no incluirán el texto recibido, sus fragmentos ni representaciones derivadas.

## Argumentos y comillas

El intérprete de comandos separa argumentos antes de que la CLI los reciba. Para proporcionar un texto con espacios, la persona usuaria debe entrecomillarlo según su shell. Ejemplo en PowerShell:

```powershell
slug-generator "Guía rápida de TypeScript"
```

La v1 no reconstruye varios argumentos como un solo texto: `slug-generator Guia rapida` es un error de uso con `E_USAGE_TOO_MANY_ARGUMENTS`. Esto elimina ambigüedad entre una entrada con espacios y un uso incorrecto de la interfaz.

## Ejemplos normativos

| Texto de entrada                | Resultado o diagnóstico     |
| ------------------------------- | --------------------------- |
| `Hola Mundo`                    | `hola-mundo`                |
| `  Guía rápida de TypeScript  ` | `guia-rapida-de-typescript` |
| `Café, té y azúcar`             | `cafe-te-y-azucar`          |
| `API_v2: novedades`             | `api-v2-novedades`          |
| `Rock & Roll!!!`                | `rock-roll`                 |
| `Málaga—Sevilla / 2026`         | `malaga-sevilla-2026`       |
| `c++ guía`                      | `c-guia`                    |
| `uno___---///dos`               | `uno-dos`                   |
| `  --Hola--  `                  | `hola`                      |
| `Straße & Æsir`                 | `strasse-aesir`             |
| `uno中文dos`                    | `uno-dos`                   |
| `中文`                          | `E_INPUT_NOT_NORMALIZABLE`  |
| `  ---  `                       | `E_INPUT_NOT_NORMALIZABLE`  |
| cadena vacía                    | `E_INPUT_EMPTY`             |
| solo espacios Unicode           | `E_INPUT_EMPTY`             |

## Colisiones

La transformación es canónica pero no garantiza unicidad. `Café` y `Cafe` producen `cafe`; `A/B` y `A B` producen `a-b`. La v1 no consulta ni mantiene un conjunto de slugs y no modifica el resultado con números, hashes o fechas. Cualquier consumidor que requiera unicidad debe resolverla fuera de la utilidad.

## Accesibilidad y operación local

La CLI futura usará texto plano y canales estándar. No dependerá de color, emojis, animación, interacción ni secuencias de control para distinguir éxito, ayuda o error. La salida correcta irá a salida estándar; ayuda y errores seguirán la tabla de interfaz. El proceso no requerirá red, credenciales ni secretos.

## Criterios de aceptación de Fase 1

- La secuencia de normalización, el alfabeto de salida y el patrón resultante son inequívocos.
- Los casos de Unicode, marcas combinantes, tabla latina mínima, símbolos y fronteras de palabra tienen una regla y ejemplos normativos.
- Los argumentos admitidos, la ayuda, los argumentos múltiples, los errores y los códigos de salida están cerrados.
- Cada escenario de entrada del catálogo [ESCENARIOS_FASE_1.md](ESCENARIOS_FASE_1.md) tiene una salida o diagnóstico único.
- La especificación confirma que no hay implementación, dependencia, fixture ejecutable ni configuración funcional en esta fase.

## Decisiones aplazadas

- Opciones para conservar Unicode, elegir separador, limitar longitud o definir diccionarios de sustitución.
- Transliteración ampliada o dependiente de idioma.
- Procesamiento de lotes, archivos, entrada estándar, modo interactivo o API.
- Detección de colisiones, persistencia, sufijos automáticos o integraciones externas.
- Formatos alternativos de salida, color, telemetría o configuración mediante entorno.
