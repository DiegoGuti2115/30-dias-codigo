# Contrato v1 — Política de contraseña, interfaz y privacidad

## Propósito

Este contrato fija el comportamiento de la primera versión del Validador de políticas de contraseña antes de crear fixtures, resultados de referencia o lógica funcional. La v1 realiza una única evaluación local y efímera contra una política fija, comunica el cumplimiento de las reglas sin revelar la entrada y no requiere red, credenciales, archivos de configuración ni servicios externos.

## Principios de seguridad y alcance

- La contraseña es un dato sensible y solo puede existir durante la interacción y la evaluación necesaria para producir el resultado.
- La herramienta no escribe, registra, transmite, serializa ni incorpora la contraseña a mensajes, excepciones, pruebas, fixtures, referencias, ejemplos o recursos de demostración.
- La entrada no se acepta como argumento, variable de entorno, archivo, entrada estándar, opción de línea de comandos ni configuración persistente.
- La v1 no realiza conexiones de red ni consultas a APIs, listas de filtraciones, diccionarios o proveedores externos.
- La v1 comprueba conformidad con una política local; no estima entropía, no garantiza resistencia frente a ataques y no sustituye una política de seguridad organizativa.
- Una ejecución evalúa una única contraseña con una única política v1 fija. No hay perfiles ni umbrales configurables.
- La biblioteca estándar de Python es la única base prevista para la implementación.

## Política v1

La contraseña es válida únicamente cuando satisface todas las reglas siguientes, en este orden estable:

| Orden | Identificador | Regla | Resultado cuando no se cumple |
|:---:|---|---|---|
| 1 | `length` | Contiene entre 12 y 128 caracteres Unicode, ambos límites incluidos. | No cumple la longitud requerida. |
| 2 | `uppercase` | Contiene al menos una letra Unicode mayúscula. | Falta una letra mayúscula. |
| 3 | `lowercase` | Contiene al menos una letra Unicode minúscula. | Falta una letra minúscula. |
| 4 | `digit` | Contiene al menos un dígito decimal Unicode. | Falta un dígito decimal. |
| 5 | `special` | Contiene al menos un carácter especial permitido. | Falta un carácter especial. |

El resultado global es **válido** si y solo si las cinco reglas se cumplen y no hay espacios en blanco. Si falla una o más reglas o existe algún espacio en blanco, el resultado global es **no válido**. La evaluación no termina al detectar el primer incumplimiento: debe determinar el estado de todas las reglas y la condición de espacios para comunicar un resultado completo y determinista.

Los identificadores, el orden, los textos de resultado y los límites de esta tabla forman parte del contrato v1. Las futuras fases podrán representarlos internamente, pero no podrán modificarlos de forma implícita.

## Definición de caracteres y Unicode

La evaluación trabaja sobre una cadena Unicode ya recibida por el mecanismo de entrada local. La longitud se mide en caracteres Unicode de la cadena, no en bytes ni en unidades visibles de interfaz.

| Categoría | Definición contractual |
|---|---|
| Letra mayúscula | Carácter para el que la clasificación Unicode de Python identifica una letra mayúscula. |
| Letra minúscula | Carácter para el que la clasificación Unicode de Python identifica una letra minúscula. |
| Dígito decimal | Carácter para el que la clasificación Unicode de Python identifica un dígito decimal. |
| Carácter especial permitido | Carácter Unicode que no es espacio en blanco, no es letra Unicode y no es dígito decimal. Incluye símbolos y puntuación admitidos por el entorno de entrada. |
| Espacio en blanco | Cualquier carácter Unicode clasificado como espacio en blanco. No satisface ninguna categoría y hace que la entrada sea inválida. |

Una letra que no sea clasificable como mayúscula ni minúscula no satisface por sí sola las reglas `uppercase` ni `lowercase`. Un número Unicode que no sea un dígito decimal no satisface la regla `digit`. Los caracteres combinantes cuentan para la longitud, pero no satisfacen por sí mismos una categoría de letra, dígito o carácter especial.

No se realizará normalización Unicode, recorte de espacios ni transformación de mayúsculas, minúsculas o dígitos. La entrada se evalúa exactamente como se introduce. Esto evita alterar silenciosamente un secreto y mantiene resultados reproducibles.

## Valores vacíos, espacios y entradas no admisibles

- Una entrada vacía es admisible para evaluación y no cumple las cinco reglas de la política v1.
- Una entrada formada solo por espacios en blanco es admisible para evaluación, incumple la regla `length` si procede, no satisface ninguna categoría y además incumple la condición de ausencia de espacios en blanco.
- Cualquier entrada que contenga uno o más espacios en blanco es **no válida**, aunque satisfaga las cinco reglas de la tabla. El resultado deberá incluir un diagnóstico adicional de espacio no permitido, situado después de las cinco reglas principales.
- La condición de espacio en blanco es una restricción de admisibilidad de la política, no un sexto identificador de regla configurable en v1.
- La entrada se considera no disponible, no inválida, cuando la persona usuaria cancela la solicitud, se alcanza fin de entrada o el entorno no puede proporcionar una lectura sin eco. En ese caso no se evalúa ningún valor.

La distinción entre entrada evaluable y entrada no disponible permite informar de un incumplimiento de política sin confundirlo con un fallo de interacción.

## Resultado previsto y mensajes permitidos

La futura representación interna deberá expresar, como mínimo, el estado global, el estado de cada regla principal en el orden definido y la condición de espacio en blanco. No incluirá la contraseña, su longitud exacta, una versión parcial, un hash ni otra representación derivada que permita relacionar resultados con una entrada concreta.

La salida de una evaluación completada podrá usar únicamente mensajes que describan el estado global y los requisitos de la política. Como mínimo, deberá poder comunicar estas condiciones:

| Situación | Mensaje permitido |
|---|---|
| Todas las reglas y la condición de espacios se cumplen | Contraseña válida según la política v1. |
| Falla una o más reglas | Contraseña no válida según la política v1. |
| Longitud fuera de rango | No cumple la longitud requerida. |
| Ausencia de mayúscula | Falta una letra mayúscula. |
| Ausencia de minúscula | Falta una letra minúscula. |
| Ausencia de dígito decimal | Falta un dígito decimal. |
| Ausencia de carácter especial | Falta un carácter especial. |
| Presencia de espacio en blanco | No se permiten espacios en blanco. |

La implementación futura puede añadir etiquetas estáticas, marcadores de estado y ayuda de uso, siempre que no reproduzca ni derive contenido de la contraseña. No se mostrarán la longitud real, categorías detectadas, posiciones, caracteres concretos ni fragmentos de la entrada.

## Interfaz de línea de comandos definida

La interfaz futura tendrá esta única forma:

```text
python src/main.py check
```

| Elemento | Obligatorio | Comportamiento definido |
|---|:---:|---|
| `check` | Sí | Subcomando único de la v1; solicita y evalúa una única contraseña de forma local. |
| Argumentos adicionales | No permitidos | Producen un mensaje de uso sin evaluar ninguna entrada. |

La contraseña se solicitará mediante un mecanismo de entrada sin eco proporcionado por la biblioteca estándar. La implementación deberá preferir el mecanismo equivalente a `getpass` y no ofrecer un modo alternativo que acepte la contraseña de forma visible, incluida una opción de argumento, una lectura de `stdin` o una variable de entorno.

Si el terminal, la consola integrada o el contexto no interactivo no permiten una lectura sin eco, la ejecución debe fallar de forma segura. No se permitirá continuar con una advertencia que pueda mostrar la contraseña en pantalla. El mensaje describirá la imposibilidad de solicitar una contraseña de forma segura, sin incluir datos de entrada.

La v1 no tiene modo demostración, confirmación interactiva, archivo de política, lectura por lote, entrada estándar, opciones de configuración ni salida a archivo. Cualquier capacidad de ese tipo queda aplazada.

## Salidas y códigos de retorno

| Situación | Salida estándar | Salida de error | Código |
|---|---|---|:---:|
| Contraseña válida | Estado global y reglas en orden estable, sin secreto. | Vacía. | `0` |
| Contraseña evaluada pero no válida | Estado global y reglas incumplidas en orden estable, sin secreto. | Vacía. | `1` |
| Argumentos incompletos, no permitidos o subcomando inválido | Vacía. | Mensaje de uso accionable. | `2` |
| Entrada cancelada, fin de entrada o lectura sin eco no disponible | Vacía. | Error breve de interacción segura. | `1` |
| Error inesperado controlable | Vacía. | Error breve sin traza ni secreto. | `1` |

Los errores previsibles no mostrarán trazas internas. La salida correcta y la salida de error no incluirán la contraseña ni la interpolarán, incluso si una biblioteca del sistema devuelve una excepción cuyo texto la contenga. La implementación deberá reemplazar ese detalle por el mensaje seguro definido en este contrato.

## No persistencia y manejo de errores

- La aplicación no creará, modificará ni leerá archivos de datos durante la evaluación normal.
- No usará logging para la contraseña, sus propiedades, errores de validación o entradas canceladas.
- No almacenará resultados ni entradas entre ejecuciones.
- No incorporará la entrada a objetos de excepción, formatos de diagnóstico, argumentos de subprocesos o salidas de depuración.
- La contraseña deberá dejar de estar referenciada tan pronto como la evaluación y la construcción del resultado lo permitan; Python no garantiza borrado físico de memoria, por lo que este contrato exige minimización de referencias, no una garantía de borrado seguro de memoria.
- Los tests futuros podrán crear valores efímeros dentro del propio proceso de prueba, pero no deberán escribirlos en archivos versionados, nombres de casos, snapshots, fixtures, salidas esperadas ni mensajes de aserción.

## Casos explícitamente fuera de alcance

- Comprobación de contraseñas filtradas, listas de diccionario, patrones comunes, secuencias, repetición, historia o reutilización.
- Cálculo de entropía, puntuación de fortaleza, recomendaciones personalizadas o generación de contraseñas.
- Hash, cifrado, autenticación, autorización, almacenamiento de credenciales, rotación o recuperación.
- Políticas configurables, perfiles organizativos, archivos de configuración o variables de entorno.
- APIs, red, cloud, bases de datos, telemetría, auditoría, interfaz web o integraciones con proveedores de identidad.
- Entrada por archivo, tubería, argumento, variable de entorno o varios valores por ejecución.
- Garantías de borrado seguro de memoria proporcionadas por el intérprete o el sistema operativo.

## Criterios de aceptación de Fase 1

- La política fija define de manera inequívoca sus límites, categorías, orden y resultado global.
- Unicode, caracteres combinantes, espacios en blanco, entradas vacías y límites de longitud tienen un tratamiento documentado.
- La interfaz acepta un único subcomando y no define ningún canal visible o persistente para suministrar la contraseña.
- Cada salida, error previsible y código de retorno tiene un comportamiento seguro y documentado.
- La documentación prohíbe la exposición de la entrada y define cómo actuar si no hay un terminal con lectura sin eco.
- El contrato permite diseñar escenarios futuros mediante categorías y resultados, sin versionar contraseñas.
- Esta fase no añade implementación funcional, dependencia, fixture, referencia ni configuración ejecutable.

## Decisiones aplazadas

- Umbrales alternativos y perfiles de política configurables.
- Políticas de frases de contraseña, espacios permitidos o requisitos de longitud distintos.
- Perfiles de Unicode específicos por organización o plataforma.
- Integración explícita y con privacidad controlada contra servicios de contraseñas comprometidas.
- Generación de sugerencias, cálculo de fortaleza o análisis de patrones.
- API, interfaz gráfica, automatización por lotes o integración con gestores de identidad.
