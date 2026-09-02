# Contrato v1 — Generador de índice Markdown

## Propósito

Este contrato fija el comportamiento de la primera versión antes de crear fixtures o implementar lógica. Cubre un único documento Markdown local, la extracción de encabezados ATX elegibles, la generación determinista de un índice jerárquico y su sustitución limitada dentro de un bloque explícitamente delimitado.

## Principios de seguridad y alcance

- Una operación recibe exactamente una ruta de documento local.
- La versión inicial admite archivos regulares con extensión `.md` o `.markdown`, sin distinción entre mayúsculas y minúsculas.
- No se admite entrada estándar, directorios, glob, enlaces simbólicos, procesamiento por lotes ni rutas de salida independientes.
- La lectura y la escritura usan UTF-8 estricto. Un byte order mark inicial se conserva si existe; no forma parte del contenido interpretado.
- La vista previa nunca persiste cambios.
- La actualización solo puede sustituir el contenido situado entre el delimitador de inicio y el de fin del único bloque de índice válido.
- El texto exterior al bloque, los delimitadores, la convención de salto de línea y la existencia o ausencia del salto final se preservan.
- La primera versión usa únicamente la biblioteca estándar y no requiere red, secretos, configuración ni servicios externos.

## Documento admitido

Un documento admisible es un archivo regular Markdown local, legible y decodificable como UTF-8. El documento puede estar vacío, no contener encabezados o tener un bloque de índice vacío; esas situaciones no son errores de sintaxis por sí mismas.

No forman parte del contrato v1 los encabezados Setext, HTML embebido, inclusiones, extensiones de proveedor, atributos, directivas, tablas de contenido de terceros ni análisis de enlaces existentes.

## Encabezados ATX

### Gramática v1

Un encabezado elegible ocupa una sola línea y cumple estas condiciones:

1. Puede comenzar con hasta tres espacios ASCII de sangría.
2. Le sigue una secuencia de una a seis almohadillas consecutivas.
3. Debe existir al menos un espacio ASCII o tabulador entre esa secuencia y el texto.
4. El texto, tras quitar espacios horizontales externos y una secuencia opcional de cierre formada por espacios horizontales y una o más almohadillas, no puede quedar vacío.
5. El nivel del encabezado es el número de almohadillas iniciales, entre 1 y 6.

Las líneas que parecen encabezados pero no cumplen esta gramática se tratan como contenido normal y no generan diagnóstico individual en v1. Una línea con siete o más almohadillas iniciales, sin espacio tras las almohadillas o sin texto no es un encabezado elegible.

### Texto del encabezado

El texto visible conservado en el índice es el texto elegible tras retirar la sintaxis ATX exterior descrita arriba. No se interpreta Markdown en línea: enlaces, énfasis, código, entidades y cualquier otra sintaxis permitida por la línea se conservan literalmente como texto del enlace del índice.

Ejemplos conceptuales de texto conservado:

- Un título con puntuación mantiene dicha puntuación como etiqueta visible.
- Un título que incluya un enlace Markdown conserva la representación Markdown del enlace como etiqueta visible.
- Un título con caracteres Unicode conserva esos caracteres como etiqueta visible.

## Regiones excluidas

Los encabezados que aparezcan dentro de un bloque de código delimitado no son elegibles.

Un bloque delimitado v1 comienza con una línea que, después de hasta tres espacios ASCII de sangría, inicia con al menos tres acentos graves consecutivos o al menos tres virgulillas consecutivas. Puede contener un identificador o texto posterior. El bloque termina con una línea que, después de hasta tres espacios de sangría, contiene una secuencia de al menos la misma longitud del mismo carácter delimitador, seguida solo de espacios horizontales.

- Un delimitador de cierre de tipo o longitud insuficiente no cierra el bloque.
- Un bloque abierto sin cierre excluye todo el contenido restante del documento.
- Los delimitadores de código no se anidan en v1.
- Los encabezados en bloques indentados, citas, HTML, comentarios u otras construcciones no reciben tratamiento especial adicional: si cumplen la gramática ATX y no están dentro de un bloque delimitado, son elegibles.

## Reglas de anclas

Cada encabezado elegible genera un ancla propia y determinista. La regla no pretende reproducir perfiles específicos de plataformas Markdown.

1. Partir del texto visible del encabezado.
2. Aplicar normalización Unicode NFKD y eliminar marcas combinantes.
3. Convertir letras ASCII a minúsculas; las letras Unicode conservan su minúscula Unicode cuando exista.
4. Conservar letras y números Unicode, guiones y espacios.
5. Eliminar cualquier otro carácter, incluida puntuación, símbolos, corchetes, comillas, asteriscos, acentos graves y signos de enlace.
6. Convertir cada secuencia no vacía de espacios horizontales o guiones en un único guion ASCII.
7. Eliminar guiones iniciales y finales.
8. Si el resultado queda vacío, usar la base `seccion`.
9. Para la primera aparición de una base, usarla sin sufijo. Para cada aparición posterior de la misma base, añadir un guion y el ordinal de repetición empezando en `2`.

La contabilidad de duplicados se aplica en el orden físico de los encabezados elegibles, incluso si los títulos pertenecen a niveles distintos. El texto mostrado no se modifica por el proceso de anclaje.

## Estructura del índice

El índice se compone de una lista Markdown no ordenada. Cada entrada contiene una etiqueta visible y un enlace interno a su ancla.

- La secuencia de entradas conserva el orden físico de los encabezados.
- La primera entrada define el nivel base de presentación.
- Una entrada cuyo nivel es superior al de la entrada previa aumenta la profundidad en una unidad, aunque el salto de encabezado sea mayor que uno.
- Una entrada con el mismo nivel mantiene la profundidad actual.
- Una entrada con un nivel inferior retrocede hasta la profundidad asociada al ancestro más cercano de igual o menor nivel; si no existe, vuelve a la profundidad base.
- Cada nivel de profundidad adicional usa dos espacios ASCII de sangría.
- Si el documento no contiene encabezados elegibles, el contenido generado del índice es vacío.

Esta política evita listas con niveles vacíos y produce una salida estable ante saltos como de nivel 1 a nivel 3.

## Bloque delimitado de índice

La versión v1 reconoce exclusivamente estas líneas de delimitación, sin espacios antes o después y ocupando por sí solas una línea:

```text
<!-- markdown-toc:start -->
<!-- markdown-toc:end -->
```

El bloque válido contiene un único delimitador de inicio seguido posteriormente por un único delimitador de fin. El contenido entre ambas líneas, incluidas sus líneas, puede tener cualquier texto y será reemplazable; los propios delimitadores no se modifican.

| Situación | Diagnóstico de contrato | Actualización permitida |
|---|---|:---:|
| No hay delimitadores | Bloque de índice ausente. | No |
| Solo hay inicio o solo hay fin | Bloque de índice incompleto. | No |
| El fin aparece antes que el inicio | Bloque de índice invertido. | No |
| Hay más de un inicio o más de un fin | Bloque de índice duplicado. | No |
| Los delimitadores tienen espacios, texto adicional o sintaxis distinta | Bloque de índice inválido. | No |
| Hay exactamente un par ordenado | Bloque de índice válido. | Sí |

La herramienta no crea delimitadores, no selecciona un bloque entre varios candidatos y no modifica el documento cuando el bloque no es válido.

## Preservación y escritura segura

La propuesta de actualización se construye sustituyendo únicamente el intervalo interior del bloque válido. El contenido que precede al delimitador de inicio y el que sigue al delimitador de fin deben permanecer idénticos.

- Se detecta la convención de saltos de línea del documento. Si el documento contiene varias convenciones, se conserva la representación original fuera del bloque y el contenido nuevo usa la convención del primer salto encontrado; si no hay saltos, usa salto de línea LF para el contenido insertado.
- La existencia o ausencia de salto final se conserva.
- La actualización persistente se realizará de manera segura en una fase posterior: deberá completar una sustitución atómica en el mismo directorio o fallar sin modificar el archivo original.
- Los permisos de escritura se comprueban antes de iniciar la operación persistente.
- Una ruta que sea directorio, enlace simbólico, archivo no Markdown, inexistente o no legible se rechaza antes de interpretar el contenido.

## Interfaz de línea de comandos definida

La interfaz futura tendrá esta forma conceptual:

```text
python src/main.py <DOCUMENT_PATH> [--write]
```

| Elemento | Obligatorio | Comportamiento definido |
|---|:---:|---|
| `<DOCUMENT_PATH>` | Sí | Ruta explícita a un archivo Markdown local válido. |
| `--write` | No | Solicita persistir el reemplazo limitado al bloque válido. |
| Sin `--write` | No aplicable | Produce una vista previa y no escribe el archivo. |

La v1 no tendrá confirmación interactiva: la ausencia de `--write` es la protección predeterminada y la presencia explícita de `--write` autoriza la actualización si todas las validaciones pasan.

La vista previa presenta el documento resultante completo en la salida estándar. La actualización correcta emite un mensaje estable de éxito en la salida estándar, sin incluir el documento completo. Los errores se emiten en la salida de error sin trazas internas por defecto.

## Códigos de salida

| Situación | Salida | Código |
|---|---|:---:|
| Vista previa válida | Documento propuesto en salida estándar. | 0 |
| Actualización válida | Confirmación breve en salida estándar. | 0 |
| Argumentos incompletos o no permitidos | Mensaje de uso accionable. | 2 |
| Ruta inexistente, no regular, enlace simbólico, extensión no admitida o sin permiso de lectura | Error de entrada en salida de error. | 1 |
| Archivo no UTF-8 | Error de codificación en salida de error. | 1 |
| Bloque ausente, incompleto, invertido, duplicado o inválido | Error de contrato en salida de error. | 1 |
| Falta de permiso de escritura o fallo de persistencia esperado | Error de actualización en salida de error. | 1 |
| Error inesperado | Mensaje breve en salida de error, sin traza. | 1 |

Un documento vacío o sin encabezados elegibles puede generar una vista previa o actualización correcta siempre que el bloque delimitado sea válido. En ese caso, el interior del bloque queda vacío.

## Criterios de aceptación de Fase 1

- La gramática distingue con precisión encabezados ATX elegibles de líneas de contenido ordinario.
- Todo encabezado dentro de un bloque de código delimitado queda excluido, incluido el resto de un bloque no cerrado.
- Las reglas de anclas resuelven de forma determinista Unicode, puntuación, espacios y títulos repetidos.
- La política de jerarquía especifica de forma única los saltos de nivel.
- Los delimitadores válidos e inválidos tienen diagnóstico, cardinalidad y comportamiento de escritura definidos.
- La protección predeterminada es una vista previa; solo `--write` puede solicitar persistencia.
- El contrato prohíbe modificaciones fuera del bloque delimitado y define la preservación de codificación y saltos de línea.
- No se introduce implementación funcional, dependencia, fixture ni configuración ejecutable durante esta fase.

## Decisiones aplazadas

- Perfiles de anclas compatibles con GitHub, GitLab u otros proveedores.
- Selección configurable de niveles, exclusiones y estilo del índice.
- Soporte de encabezados Setext, HTML, MDX, front matter o extensiones de Markdown.
- Inserción automática de delimitadores, múltiples índices por documento o bloques con identificadores.
- Procesamiento de directorios, copias de seguridad configurables, diferencias visuales e integración de control de versiones.
- Verificación y reparación de enlaces internos o externos.
