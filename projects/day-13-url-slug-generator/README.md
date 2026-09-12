# Día 13 — Generador de slugs

> Microproyecto CLI del reto [30 Días, 30 Proyectos](../../README.md). **Estado:** versión 1 completada: contrato, entorno TypeScript, núcleo puro, CLI local, validaciones automatizadas y documentación de entrega verificada.

## Propósito

Transformar un texto breve en un _slug_ estable y legible para usarlo como segmento de una URL, nombre identificable o clave de presentación. Un slug de la primera versión contendrá únicamente letras ASCII en minúscula, dígitos y guiones simples.

El proyecto resuelve la necesidad de normalizar títulos y etiquetas de forma predecible, evitando que una URL dependa de espacios, mayúsculas, tildes o símbolos.

## Alcance de la versión 1

- Exponer una utilidad de línea de comandos escrita en TypeScript.
- Recibir una única cadena de texto por argumento de la CLI.
- Generar un único slug determinista y escribirlo en la salida estándar.
- Normalizar espacios, separadores comunes, mayúsculas, acentos latinos y símbolos no permitidos según las reglas de esta especificación.
- Informar un error comprensible y un código de salida distinto de cero cuando la entrada sea ausente, no textual o no produzca contenido válido.
- Incluir pruebas unitarias del núcleo y pruebas de integración de la CLI que verifiquen el contrato de proceso.

## Fuera de alcance

- Generar identificadores únicos, consultar una base de datos o resolver colisiones automáticamente.
- Persistir slugs, editar archivos, procesar lotes, leer desde entrada estándar o exponer una API HTTP.
- Transliterar de manera exhaustiva alfabetos no latinos, traducir texto, detectar idioma o hacer SEO semántico.
- Configuración mediante secretos, servicios externos, telemetría o una interfaz gráfica.
- Opciones avanzadas de longitud, sufijo, diccionario personalizado o preservación de Unicode en la versión 1.

## Tecnología y restricciones

La planificación raíz asigna a este proyecto la categoría **CLI** y el stack **TypeScript**. La Fase 2 fija Node.js 22 o superior, npm 10 o superior, TypeScript, el runner de pruebas integrado de Node.js y Prettier para el formato de configuración. Las instrucciones reproducibles, dependencias justificadas y comandos disponibles están en [docs/ENTORNO_FASE_2.md](docs/ENTORNO_FASE_2.md).

No hay integraciones externas ni variables de entorno previstas. Por ello no se requiere archivo de ejemplo de variables. La ejecución será local y determinista, que actúa como ruta principal y fallback intrínseco.

## Interfaz de línea de comandos

La CLI compilada está disponible como binario local con esta forma:

```text
slug-generator <texto>
```

- `<texto>` es un único valor textual obligatorio. Si contiene espacios, el intérprete de comandos debe recibirlo entre comillas.
- La salida correcta contiene únicamente el slug seguido de un salto de línea.
- Los diagnósticos se escriben en la salida de error y no mezclan texto explicativo con la salida correcta.
- La ayuda aislada se invoca con `slug-generator --help` o `slug-generator -h`.
- La ayuda, los mensajes estables y los códigos de salida están cerrados en [docs/CONTRATO_V1.md](docs/CONTRATO_V1.md).

Para una instalación limpia, compilación y comprobaciones reproducibles, siga [docs/USO_LOCAL.md](docs/USO_LOCAL.md). Tras compilar con `npm run build`, puede ejecutarse directamente con Node.js:

```powershell
node dist/cli.js "Guía rápida de TypeScript"
```

También queda declarado el binario `slug-generator` en [package.json](package.json) para su uso como paquete local instalado.

### Ejemplos

| Entrada textual                 | Salida esperada                             |
| ------------------------------- | ------------------------------------------- |
| `Hola Mundo`                    | `hola-mundo`                                |
| `  Guía rápida de TypeScript  ` | `guia-rapida-de-typescript`                 |
| `Café, té y azúcar`             | `cafe-te-y-azucar`                          |
| `API_v2: novedades`             | `api-v2-novedades`                          |
| `Rock & Roll!!!`                | `rock-roll`                                 |
| `Málaga—Sevilla / 2026`         | `malaga-sevilla-2026`                       |
| `niño`                          | `nino`                                      |
| `Crème brûlée`                  | `creme-brulee`                              |
| `  ---  `                       | error de entrada sin contenido normalizable |
| cadena vacía                    | error de entrada vacía                      |

Los ejemplos están cubiertos por pruebas automatizadas del núcleo y de la CLI. La herramienta no reconstruye varios argumentos: `slug-generator Guia rapida` es un error de uso.

## Reglas de normalización

Las siguientes reglas constituyen un resumen de la especificación de comportamiento. El orden normativo completo, la tabla latina mínima y la semántica exacta de las fronteras se encuentran en [docs/CONTRATO_V1.md](docs/CONTRATO_V1.md). El núcleo de [src/slug.ts](src/slug.ts) las implementa sin depender del proceso de terminal:

1. **Validar la entrada.** Solo se aceptará una cadena primitiva no vacía. Los valores ausentes, nulos, no textuales o compuestos se considerarán inválidos.
2. **Recortar extremos.** Se eliminarán los espacios en blanco iniciales y finales.
3. **Normalizar Unicode y diacríticos.** La cadena se descompondrá de forma canónica y se eliminarán las marcas diacríticas combinables. Así, `á`, `é`, `í`, `ó`, `ú`, `ü`, `ñ`, `ç` y sus variantes usuales producirán respectivamente `a`, `e`, `i`, `o`, `u`, `n`, `c` cuando su descomposición Unicode lo permita.
4. **Convertir a minúsculas.** La salida se convertirá a minúsculas de forma independiente de la capitalización original.
5. **Conservar solo el alfabeto de salida.** Se conservarán letras ASCII de `a` a `z` y dígitos de `0` a `9`. No se conservarán emojis, símbolos monetarios, puntuación, comillas, barras, caracteres de control ni caracteres de alfabetos sin transliteración definida.
6. **Unificar separadores.** Todo grupo contiguo de espacios o caracteres descartados situado entre fragmentos conservables representará un único guion. Esto incluye espacios, tabulaciones, guiones tipográficos, guiones bajos, barras, puntuación y símbolos.
7. **Eliminar guiones de borde.** No habrá guiones al inicio ni al final, ni guiones consecutivos.
8. **Comprobar el resultado.** Si después de normalizar no queda ningún carácter conservable, la operación fallará en lugar de devolver un slug vacío.

### Acentos, caracteres especiales y Unicode

La normalización de acentos se basa en descomposición Unicode y eliminación de diacríticos. El contrato además cierra una tabla mínima para determinados caracteres latinos que no se descomponen de manera útil. No se promete una transliteración universal: caracteres chinos, cirílicos, árabes o emojis se descartarán o formarán una frontera de palabra según su posición. Consulte [docs/CONTRATO_V1.md](docs/CONTRATO_V1.md) para la tabla cerrada y sus ejemplos.

Los símbolos no se concatenarán silenciosamente. Cuando separen fragmentos válidos, actuarán como una frontera de palabra; cuando aparezcan en los extremos, se eliminarán. Por ejemplo, `c++ guía` se normalizará como `c-guia`, no como `cguia`.

### Espacios y separación de palabras

Los espacios simples, múltiples y otros espacios Unicode se tratan como separadores. Cualquier secuencia de separadores se reduce a un solo guion. Los separadores visibles o técnicos, como `_`, `-`, `—`, `/` y `:`, siguen la misma regla. El resultado nunca tendrá espacios ni guiones repetidos.

## Entradas inválidas y errores previstos

| Situación                                                  | Comportamiento previsto                     |
| ---------------------------------------------------------- | ------------------------------------------- |
| Argumento ausente                                          | Error de uso; no se genera salida correcta. |
| Valor nulo o no textual en el núcleo                       | Error de validación explícito.              |
| Cadena vacía o formada solo por espacios                   | Error de validación explícito.              |
| Cadena formada solo por símbolos o caracteres descartables | Error de contenido no normalizable.         |
| Texto que genera un slug válido                            | Salida determinista y código de éxito.      |

La CLI recibirá argumentos textuales del entorno. El núcleo expone `normalizeSlug(input: unknown): string` y distingue valores nulos o no textuales mediante `SlugNormalizationError` y sus códigos estables; el adaptador CLI traducirá esos errores a sus diagnósticos y códigos de proceso. Los mensajes deberán describir la causa sin imprimir datos sensibles innecesariamente.

## Colisiones

La normalización puede producir el mismo slug para entradas distintas: `Café` y `Cafe` producen `cafe`; `A/B` y `A B` producen `a-b`. La versión 1 no detectará ni resolverá estas colisiones porque no mantiene un registro de valores existentes. La persona consumidora deberá comprobar unicidad en la capa que posea el contexto, por ejemplo añadiendo un identificador estable o un sufijo fuera de esta utilidad.

## Requisitos funcionales

- RF-01: aceptar un texto de entrada único desde la CLI prevista.
- RF-02: validar ausencia, vacío y resultado sin caracteres normalizables.
- RF-03: devolver un slug formado solo por minúsculas ASCII, dígitos y guiones simples.
- RF-04: eliminar diacríticos Unicode de los caracteres que admitan descomposición canónica.
- RF-05: convertir grupos de espacios, símbolos y separadores en una sola frontera con guion.
- RF-06: evitar guiones iniciales, finales o consecutivos.
- RF-07: mantener determinismo: igual entrada válida, igual salida.
- RF-08: separar salida correcta y diagnósticos de error.

## Requisitos no funcionales

- RNF-01: ejecución completamente local, sin red, almacenamiento ni secretos.
- RNF-02: dependencia mínima y justificada; la lógica de normalización deberá ser pura y desacoplada de la CLI.
- RNF-03: comportamiento documentado, reproducible y cubierto por pruebas automatizadas del núcleo y de integración de CLI.
- RNF-04: mensajes de uso y error claros, breves y en español.
- RNF-05: el procesamiento deberá ser lineal respecto a la longitud de la entrada para textos de título habituales.
- RNF-06: la documentación y el código futuro respetarán las convenciones del repositorio y el límite temporal del reto.

## Criterios de aceptación de la versión 1

La primera versión estará aceptada cuando se cumpla lo siguiente:

- Una instalación documentada permita invocar la CLI localmente.
- Los ejemplos de esta especificación generen los resultados indicados o el error documentado.
- La salida correcta cumpla el patrón conceptual `^[a-z0-9]+(?:-[a-z0-9]+)*$`.
- Los casos de acentos, espacios múltiples, símbolos, guiones de borde, entradas vacías y solo símbolos estén cubiertos por pruebas unitarias.
- Una prueba de integración confirme el contrato de argumento, salida estándar, salida de error y código de salida.
- No haya llamadas de red, lectura o escritura de datos de usuario, secretos ni dependencias externas necesarias para el flujo principal.
- El README, el roadmap y la ayuda de la CLI futura describan el mismo alcance.

## Estrategia de pruebas

1. **Unitarias de normalización — completadas:** [tests/slug.test.mjs](tests/slug.test.mjs) cubre mayúsculas, tildes, diacríticos en forma compuesta y descompuesta, tabla latina mínima, espacios Unicode, símbolos, separadores mezclados, dígitos y casos límite.
2. **Unitarias de validación — completadas:** la misma suite cubre valores ausentes, nulos, no textuales, vacíos, solo separadores y solo caracteres no transliterables.
3. **Propiedades o regresión — completadas:** se verifica el patrón permitido, la ausencia de guiones de borde o consecutivos, el determinismo y la idempotencia para las transformaciones válidas.
4. **Integración de CLI — completada:** [tests/cli.test.mjs](tests/cli.test.mjs) invoca el ejecutable compilado con entradas válidas e inválidas y comprueba ayuda, argumentos, opciones, salida estándar, salida de error y códigos de proceso.
5. **Revisión de entrega — completada:** la guía [docs/USO_LOCAL.md](docs/USO_LOCAL.md), la demostración [assets/DEMO_15S.md](assets/DEMO_15S.md) y la ayuda verifican una experiencia de texto plano sin dependencia de color, interacción o datos sensibles.

Las tablas de regresión residen en las suites de [tests](tests), no necesitan fixtures y no dependen del sistema operativo, la configuración regional ni la zona horaria.

## Accesibilidad y experiencia de terminal

Aunque es una CLI, la accesibilidad forma parte de su interfaz. La herramienta usa texto plano, mensajes autoexplicativos y códigos de salida consistentes; no depende de color, emojis, animación ni salida interactiva para comunicar éxito o fallo. La ayuda indica formato, ejemplo y cómo escapar espacios. Los mensajes de error no se ocultan tras secuencias de control y pueden leerse correctamente con lectores de pantalla o redirección de terminal.

## Decisiones técnicas iniciales

- **Modelo local y sin estado:** es suficiente para un conversor de una entrada y elimina integraciones que no aportan valor al objetivo atómico.
- **Salida ASCII restringida:** maximiza compatibilidad en rutas y evita ambigüedades de codificación; preservar Unicode queda fuera de la versión 1.
- **Guion como único separador:** simplifica la legibilidad y aporta una forma canónica única por familia de entradas.
- **Colisiones delegadas:** sin persistencia no existe contexto fiable para resolver unicidad; la utilidad no añadirá sufijos implícitos.
- **Lógica pura separada de la CLI:** permitirá probar la normalización sin procesos secundarios y conservar una CLI fina.
- **Contrato cerrado antes de implementar:** la interfaz, la tabla latina mínima, los mensajes y los códigos de retorno se fijan en [docs/CONTRATO_V1.md](docs/CONTRATO_V1.md) para evitar cambios implícitos en fases posteriores.

Las decisiones derivadas de detalles no especificados por el índice raíz se registran explícitamente en [docs/DECISIONES.md](docs/DECISIONES.md). El catálogo [docs/ESCENARIOS_FASE_1.md](docs/ESCENARIOS_FASE_1.md) aporta vectores documentales para las pruebas posteriores.

## Estructura del proyecto

```text
projects/day-13-url-slug-generator/
├── README.md
├── ROADMAP.md
├── package.json
├── package-lock.json
├── tsconfig.json
├── .prettierrc.json
├── docs/
│   ├── CONTRATO_V1.md
│   ├── DECISIONES.md
│   ├── ENTORNO_FASE_2.md
│   ├── ESCENARIOS_FASE_1.md
│   └── USO_LOCAL.md
├── src/
│   ├── cli.ts
│   ├── environment.d.ts
│   └── slug.ts
├── tests/
│   ├── cli.test.mjs
│   └── slug.test.mjs
├── data/
│   └── fixtures/
└── assets/
    ├── carrusel-linkedin.html
    └── DEMO_15S.md
```

| Ruta                                                           | Finalidad en esta fase                                                                                                                     |
| -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| [README.md](README.md)                                         | Especificación funcional, límites y guía de inicio.                                                                                        |
| [ROADMAP.md](ROADMAP.md)                                       | Plan por fases, dependencias y condiciones de entrega.                                                                                     |
| [docs/CONTRATO_V1.md](docs/CONTRATO_V1.md)                     | Fuente de verdad de las reglas de normalización, interfaz, mensajes y códigos de salida v1.                                                |
| [docs/DECISIONES.md](docs/DECISIONES.md)                       | Registro de decisiones adoptadas ante vacíos de especificación.                                                                            |
| [docs/ESCENARIOS_FASE_1.md](docs/ESCENARIOS_FASE_1.md)         | Vectores documentales que trazan el contrato hacia la implementación y las pruebas automatizadas.                                          |
| [docs/ENTORNO_FASE_2.md](docs/ENTORNO_FASE_2.md)               | Decisiones de runtime, instalación reproducible, scripts y límites del entorno.                                                            |
| [docs/USO_LOCAL.md](docs/USO_LOCAL.md)                         | Instalación limpia, ejecución, ayuda, errores y comprobaciones verificadas de la entrega.                                                  |
| [assets/DEMO_15S.md](assets/DEMO_15S.md)                       | Guion local breve que muestra entrada, acción, resultado y error controlado.                                                               |
| [assets/carrusel-linkedin.html](assets/carrusel-linkedin.html) | Presentación interactiva autónoma del proyecto; se abre directamente en un navegador.                                                      |
| [package.json](package.json)                                   | Manifiesto npm, versiones mínimas, herramientas y scripts de calidad y prueba.                                                             |
| [tsconfig.json](tsconfig.json)                                 | Compilación TypeScript estricta dirigida a `dist/`.                                                                                        |
| [src/environment.d.ts](src/environment.d.ts)                   | Ancla no ejecutable que conserva la verificación del entorno de Fase 2.                                                                    |
| [src/slug.ts](src/slug.ts)                                     | Núcleo puro de normalización, patrón canónico y errores de dominio estables.                                                               |
| [src/cli.ts](src/cli.ts)                                       | Adaptador de proceso que interpreta argumentos y traduce resultados o errores del núcleo a canales y códigos de salida.                    |
| [tests/slug.test.mjs](tests/slug.test.mjs)                     | Pruebas unitarias del núcleo compilado con el runner integrado de Node.js.                                                                 |
| [tests/cli.test.mjs](tests/cli.test.mjs)                       | Pruebas de proceso para argumentos, ayuda, canales de salida, errores y códigos de la CLI.                                                 |
| [tests](tests)                                                 | Directorio de pruebas unitarias y de proceso de la versión 1.                                                                              |
| [data/fixtures](data/fixtures)                                 | Reserva opcional para fixtures textuales no sensibles; no son necesarios en la versión 1.                                                  |
| [assets](assets)                                               | Recursos de entrega; incluye la demostración [DEMO_15S.md](assets/DEMO_15S.md) y el [carrusel interactivo](assets/carrusel-linkedin.html). |

Los archivos `.gitkeep` preservan en Git los directorios que continúan vacíos. El código TypeScript de dominio está aislado en [src/slug.ts](src/slug.ts), mientras que [src/environment.d.ts](src/environment.d.ts) conserva el ancla de compilación de la Fase 2.

## Estado de esta entrega

La versión 1 está completada. Las Fases 0 y 1 fijan el alcance y contrato; la Fase 2 aporta el entorno reproducible; las Fases 3 y 4 implementan el núcleo y la CLI; la Fase 5 valida el contrato con pruebas unitarias y de proceso; y la Fase 6 publica la guía de uso, la demostración y la verificación final. El alcance se mantiene local, atómico y sin estado, conforme a [ROADMAP.md](ROADMAP.md).
