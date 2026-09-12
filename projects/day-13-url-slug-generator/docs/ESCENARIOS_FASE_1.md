# Catálogo de escenarios — Fase 1

Este catálogo convierte el contrato [CONTRATO_V1.md](CONTRATO_V1.md) en vectores documentales de implementación y prueba. No es un fixture ejecutable, no requiere entorno TypeScript y no añade comportamiento fuera del contrato.

## Convenciones

- Los valores de entrada se interpretan como una única cadena ya recibida por el núcleo futuro, salvo los escenarios de interfaz CLI.
- `OK` representa una transformación correcta y el valor de `Salida` es el slug exacto.
- `ERROR` representa un rechazo; el identificador y mensaje se definen en el contrato.
- `␠` representa un espacio ASCII visible en tablas. `NBSP` representa un espacio de no separación Unicode.
- Los casos contienen datos sintéticos y no incluyen secretos ni información personal.

## Transformación, mayúsculas y acentos

| ID   | Entrada                         | Estado | Salida o diagnóstico        | Reglas cubiertas                         |
| ---- | ------------------------------- | ------ | --------------------------- | ---------------------------------------- |
| N-01 | `Hola Mundo`                    | OK     | `hola-mundo`                | Minúsculas, espacio.                     |
| N-02 | `␠␠Guía rápida de TypeScript␠␠` | OK     | `guia-rapida-de-typescript` | Recorte, acentos, espacios.              |
| N-03 | `Café, té y azúcar`             | OK     | `cafe-te-y-azucar`          | Diacríticos, puntuación.                 |
| N-04 | `À bientôt`                     | OK     | `a-bientot`                 | Mayúscula acentuada, NFKD.               |
| N-05 | `Crème brûlée`                  | OK     | `creme-brulee`              | Diacríticos combinables.                 |
| N-06 | `niño`                          | OK     | `nino`                      | `ñ` por NFKD.                            |
| N-07 | `áéíóúüñç`                      | OK     | `aeiouunc`                  | Serie de letras latinas con diacríticos. |

## Tabla latina mínima

| ID   | Entrada          | Estado | Salida           | Regla cubierta                |
| ---- | ---------------- | ------ | ---------------- | ----------------------------- |
| L-01 | `Straße`         | OK     | `strasse`        | `ß` se convierte en `ss`.     |
| L-02 | `Æsir`           | OK     | `aesir`          | `Æ` se convierte en `ae`.     |
| L-03 | `Œuvre`          | OK     | `oeuvre`         | `Œ` se convierte en `oe`.     |
| L-04 | `Øresund`        | OK     | `oresund`        | `Ø` se convierte en `o`.      |
| L-05 | `Ðagur Þór`      | OK     | `dagur-thor`     | `Ð` y `Þ`.                    |
| L-06 | `Łódź Đuro`      | OK     | `lodz-duro`      | `Ł` y `Đ`; `ź` por NFKD.      |
| L-07 | `İstanbul ıslak` | OK     | `istanbul-islak` | `İ` por NFKD e `ı` por tabla. |

## Símbolos, puntuación y separadores

| ID   | Entrada                 | Estado | Salida                | Regla cubierta                                          |
| ---- | ----------------------- | ------ | --------------------- | ------------------------------------------------------- |
| S-01 | `API_v2: novedades`     | OK     | `api-v2-novedades`    | Guion bajo y dos puntos.                                |
| S-02 | `Rock & Roll!!!`        | OK     | `rock-roll`           | Símbolo y puntuación terminal.                          |
| S-03 | `Málaga—Sevilla / 2026` | OK     | `malaga-sevilla-2026` | Raya, barra, dígitos.                                   |
| S-04 | `c++ guía`              | OK     | `c-guia`              | Símbolos como frontera.                                 |
| S-05 | `uno___---///dos`       | OK     | `uno-dos`             | Grupo mixto de separadores.                             |
| S-06 | `--Hola--`              | OK     | `hola`                | Separadores de borde.                                   |
| S-07 | `a\tb\nc`               | OK     | `a-b-c`               | Tabulador y salto de línea internos.                    |
| S-08 | `unoNBSPdos`            | OK     | `uno-dos`             | Espacio Unicode; sustituir `NBSP` por U+00A0 al probar. |
| S-09 | `Precio € 10`           | OK     | `precio-10`           | Símbolo monetario.                                      |

## Unicode no transliterado

| ID   | Entrada         | Estado | Salida o diagnóstico       | Regla cubierta                      |
| ---- | --------------- | ------ | -------------------------- | ----------------------------------- |
| U-01 | `uno中文dos`    | OK     | `uno-dos`                  | Carácter descartado crea frontera.  |
| U-02 | `привет mundo`  | OK     | `mundo`                    | Texto no ASCII de borde descartado. |
| U-03 | `hola 😀 mundo` | OK     | `hola-mundo`               | Emoji como frontera.                |
| U-04 | `中文`          | ERROR  | `E_INPUT_NOT_NORMALIZABLE` | Sin contenido conservable.          |
| U-05 | `😀---💡`       | ERROR  | `E_INPUT_NOT_NORMALIZABLE` | Símbolos sin contenido conservable. |

## Entradas inválidas del núcleo

| ID   | Entrada                      | Estado | Diagnóstico                | Regla cubierta        |
| ---- | ---------------------------- | ------ | -------------------------- | --------------------- |
| E-01 | cadena vacía                 | ERROR  | `E_INPUT_EMPTY`            | Vacío.                |
| E-02 | `␠␠␠`                        | ERROR  | `E_INPUT_EMPTY`            | Solo espacios ASCII.  |
| E-03 | `NBSP`                       | ERROR  | `E_INPUT_EMPTY`            | Solo espacio Unicode. |
| E-04 | `---`                        | ERROR  | `E_INPUT_NOT_NORMALIZABLE` | Solo separadores.     |
| E-05 | `!!!`                        | ERROR  | `E_INPUT_NOT_NORMALIZABLE` | Solo puntuación.      |
| E-06 | `null` como valor no textual | ERROR  | `E_INPUT_NOT_TEXT`         | Nulo.                 |
| E-07 | `42` como valor no textual   | ERROR  | `E_INPUT_NOT_TEXT`         | Número.               |
| E-08 | `{}` como valor no textual   | ERROR  | `E_INPUT_NOT_TEXT`         | Objeto.               |

## Interfaz de CLI

| ID   | Invocación conceptual             | Estado | Salida esperada               | Error esperado               | Código |
| ---- | --------------------------------- | ------ | ----------------------------- | ---------------------------- | :----: |
| C-01 | `slug-generator "Hola Mundo"`     | OK     | `hola-mundo` + salto de línea | Vacía                        |  `0`   |
| C-02 | `slug-generator --help`           | OK     | Ayuda exacta del contrato     | Vacía                        |  `0`   |
| C-03 | `slug-generator -h`               | OK     | Ayuda exacta del contrato     | Vacía                        |  `0`   |
| C-04 | `slug-generator`                  | ERROR  | Vacía                         | `E_USAGE_MISSING_TEXT`       |  `2`   |
| C-05 | `slug-generator Guia rapida`      | ERROR  | Vacía                         | `E_USAGE_TOO_MANY_ARGUMENTS` |  `2`   |
| C-06 | `slug-generator --unicode "Hola"` | ERROR  | Vacía                         | `E_USAGE_UNKNOWN_OPTION`     |  `2`   |
| C-07 | `slug-generator --help extra`     | ERROR  | Vacía                         | `E_USAGE_TOO_MANY_ARGUMENTS` |  `2`   |
| C-08 | `slug-generator "---"`            | ERROR  | Vacía                         | `E_INPUT_NOT_NORMALIZABLE`   |  `1`   |
| C-09 | `slug-generator "   "`            | ERROR  | Vacía                         | `E_INPUT_EMPTY`              |  `1`   |

## Trazabilidad para fases posteriores

- La Fase 2 podrá convertir este catálogo a fixtures de datos sin cambiar resultados ni identificadores.
- La Fase 3 deberá cubrir `N-*`, `L-*`, `S-*`, `U-*` y `E-*` con pruebas del núcleo puro.
- La Fase 4 deberá implementar la interpretación y canales definidos en `C-*`.
- La Fase 5 deberá automatizar los escenarios y verificar salida estándar, salida de error y códigos de proceso.
- Si se modifica un vector, deberá actualizarse el contrato y explicar el cambio en [DECISIONES.md](DECISIONES.md).
