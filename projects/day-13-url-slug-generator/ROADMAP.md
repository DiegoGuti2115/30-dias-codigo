# Roadmap — Generador de slugs

Este roadmap organiza el desarrollo del proyecto 13 como una utilidad CLI TypeScript local, atómica y sin estado. Las **Fases 0 y 1** están completadas documentalmente: preparan estructura y contrato sin crear código de implementación, configuración ejecutable ni pruebas ejecutables.

## Objetivo de la versión 1

Entregar una CLI que reciba un texto y devuelva un slug determinista en minúsculas ASCII, compuesto por letras, dígitos y guiones simples. La normalización, los errores y los límites están definidos en [README.md](README.md) y las decisiones derivadas se registran en [docs/DECISIONES.md](docs/DECISIONES.md).

## Prioridad y límites

**Prioridad P0:** flujo local de una sola entrada, normalización determinista y diagnóstico claro de entradas inválidas.

**Fuera de P0:** unicidad, almacenamiento, API, interfaz gráfica, lotes, lectura de archivos, entrada estándar, opciones configurables, transliteración exhaustiva de alfabetos no latinos e integraciones externas.

## Estado de las fases

- [x] **Fase 0 — Preparación documental y estructural:** completada en esta tarea.
- [x] **Fase 1 — Cierre del contrato de normalización y CLI:** completada documentalmente.
- [x] **Fase 2 — Entorno TypeScript y calidad:** completada.
- [x] **Fase 3 — Implementación del núcleo de normalización:** completada.
- [x] **Fase 4 — Adaptador de línea de comandos:** completada.
- [x] **Fase 5 — Validaciones y pruebas automatizadas:** completada.
- [x] **Fase 6 — Documentación de uso, calidad y entrega:** completada.

## Dependencias entre fases

```text
Fase 0 → Fase 1 → Fase 2 → Fase 3 → Fase 4 → Fase 5 → Fase 6
                         │        │        │
                         │        └────────┴── pruebas unitarias e integración
                         └── entorno y herramientas de calidad
```

- La Fase 1 es la fuente de verdad para reglas, errores e interfaz de las fases posteriores.
- La Fase 2 habilita compilación, ejecución local y herramientas de calidad, pero no sustituye las pruebas.
- La Fase 3 depende de las reglas cerradas y debe permanecer independiente del proceso de terminal.
- La Fase 4 depende del núcleo de la Fase 3 y no duplicará reglas de normalización.
- La Fase 5 valida tanto el núcleo como el contrato de CLI después de que existan.
- La Fase 6 requiere que la versión P0 haya aprobado las verificaciones anteriores.

## Fase 0 — Preparación documental y estructural — Completada

**Objetivo:** reservar la ubicación del proyecto y fijar un alcance implementable sin adelantar lógica funcional.

**Tareas realizadas:**

- Revisar el índice raíz, el stack asignado al día 13, la estructura estándar y los proyectos existentes disponibles como referencia.
- Crear [README.md](README.md) en español con propósito, alcance, reglas de normalización, casos límite, requisitos, accesibilidad, aceptación y pruebas planificadas.
- Crear este roadmap y el registro [docs/DECISIONES.md](docs/DECISIONES.md).
- Reservar [src](src), [tests](tests), [data/fixtures](data/fixtures) y [assets](assets) con archivos `.gitkeep` cuando son necesarios para conservar directorios vacíos.

**Dependencias:** ninguna.

**Criterios de finalización verificables:**

- Los documentos describen un generador de slugs CLI TypeScript compatible con el proyecto 13 del índice raíz.
- La estructura coincide con la convención `src`, `tests`, `data`, `assets`, `README.md` y manifiesto futuro por proyecto.
- No existen archivos TypeScript, JavaScript, funciones, clases, componentes, pruebas ejecutables, manifiestos de paquetes ni configuración funcional.
- Las decisiones no definidas por el índice raíz se distinguen como decisiones locales documentadas.

## Fase 1 — Cierre del contrato de normalización y CLI — Completada, P0

**Objetivo:** consolidar una especificación precisa que permita implementar sin ambigüedad.

**Entregables completados:**

- [docs/CONTRATO_V1.md](docs/CONTRATO_V1.md) como fuente de verdad para la secuencia de normalización, alfabeto de salida, tabla latina mínima, tratamiento de Unicode, símbolos, argumentos, ayuda, mensajes y códigos de salida.
- [docs/ESCENARIOS_FASE_1.md](docs/ESCENARIOS_FASE_1.md) con vectores documentales de transformación, errores del núcleo e integración futura de la CLI.
- Actualización de [README.md](README.md) para enlazar el contrato cerrado y distinguir el trabajo documental del trabajo todavía pendiente.

**Decisiones cerradas:**

- Se usará `NFKD`, eliminación de marcas combinantes y una tabla latina mínima explícita para `ß`, `æ`, `œ`, `ø`, `ð`, `þ`, `ł`, `đ` e `ı`.
- Todo grupo de caracteres no conservables entre fragmentos ASCII válidos será una sola frontera con guion; los grupos de borde se descartan.
- La CLI admitirá exactamente un argumento `<texto>` o la ayuda aislada `--help`/`-h`; no reconstruirá varios argumentos.
- Los códigos son `0` para resultado o ayuda correctos, `2` para uso incorrecto y `1` para contenido inválido o fallo controlable.
- Las entradas sin contenido normalizable se rechazan; no se devuelve un slug vacío.

**Dependencias:** Fase 0.

**Criterios de finalización verificables:**

- Completado: cada caso válido o inválido dispone de salida o diagnóstico inequívoco en el contrato y catálogo.
- Completado: el contrato exige el patrón `^[a-z0-9]+(?:-[a-z0-9]+)*$` para toda salida válida.
- Completado: quedan documentadas las decisiones sobre Unicode no latino, argumentos adicionales, ayuda, mensajes y códigos.
- Completado: no se introdujo implementación, dependencia, fixture ejecutable ni configuración funcional.

## Fase 2 — Entorno TypeScript y calidad — Completada, P0

**Objetivo:** preparar una base reproducible y mínima para desarrollar y comprobar la utilidad.

**Entregables completados:**

- Runtime mínimo Node.js 22 y npm 10, justificados en [docs/ENTORNO_FASE_2.md](docs/ENTORNO_FASE_2.md) y declarados en [package.json](package.json).
- Manifiesto npm y [package-lock.json](package-lock.json) con tres dependencias de desarrollo: TypeScript, tipos de Node.js y Prettier.
- [tsconfig.json](tsconfig.json) estricto con compilación NodeNext hacia `dist/`, junto con [src/environment.d.ts](src/environment.d.ts) como ancla no ejecutable de comprobación.
- Scripts `build`, `typecheck`, `test`, `format`, `format:check` y `quality`. El script de pruebas verifica que el runner integrado queda operativo aunque no añade escenarios funcionales antes de la Fase 5.
- Formato mínimo mediante [`.prettierrc.json`](.prettierrc.json). Las exclusiones existentes de la raíz ya cubren `node_modules/`, `dist/` y `*.tsbuildinfo`, por lo que no fue necesario un `.gitignore` local.

**Verificaciones ejecutadas:**

- `npm install`: instalación local sin vulnerabilidades notificadas.
- `npm run format`: formato aplicado a la configuración y al ancla TypeScript.
- `npm run quality`: comprobación de tipos y formato aprobados.
- `npm run build`: compilación TypeScript aprobada.
- `npm test`: runner de Node.js operativo, sin pruebas de comportamiento todavía (`0` pruebas, `0` fallos).

**Dependencias:** Fase 1.

**Criterios de finalización verificables:**

- Completado: el entorno se instala desde instrucciones reproducibles y sin secretos.
- Completado: las dependencias son mínimas, justificadas y compatibles con la CLI local.
- Completado: los comandos de calidad están documentados y se ejecutan contra una estructura mínima.
- Completado: no se añadió integración externa ni configuración cloud.

**Límite de fase:** no existe todavía un comando de ejecución de la utilidad, porque el núcleo y el adaptador de terminal se implementarán en las Fases 3 y 4. No se añadieron pruebas de escenarios, que pertenecen a la Fase 5.

## Fase 3 — Implementación del núcleo de normalización — Completada, P0

**Objetivo:** implementar la transformación pura y validable que convierte texto en slug.

**Entregables completados:**

- Módulo de dominio [src/slug.ts](src/slug.ts) con la API pública `normalizeSlug(input: unknown): string`, el patrón `SLUG_PATTERN` y los errores estables `SlugNormalizationError`.
- Validación de cadenas primitivas, recorte Unicode y rechazos con los códigos `E_INPUT_NOT_TEXT`, `E_INPUT_EMPTY` y `E_INPUT_NOT_NORMALIZABLE` definidos por el contrato.
- Normalización `NFKD`, eliminación de marcas combinantes, minúsculas Unicode, tabla latina mínima explícita, filtrado ASCII y consolidación determinista de fronteras con guion.
- Pruebas unitarias en [tests/slug.test.mjs](tests/slug.test.mjs), ejecutadas sobre la compilación TypeScript sin introducir un adaptador CLI.
- Actualización de scripts npm para compilar antes de probar e incluir el módulo y la suite en las comprobaciones de formato.

**Verificaciones ejecutadas:**

- `npm run format`: formato aplicado al núcleo y a las pruebas.
- `npm run quality`: comprobaciones de tipos y formato aprobadas.
- `npm test`: compilación aprobada y 40 pruebas superadas, sin fallos.

**Dependencias:** Fases 1 y 2.

**Criterios de finalización verificables:**

- Completado: el núcleo ofrece una interfaz pública separada de la CLI y no realiza entrada/salida, llamadas de red, persistencia ni uso de estado global.
- Completado: los casos de normalización, la tabla latina mínima y los rechazos de dominio se comprueban automáticamente.
- Completado: toda salida válida satisface el patrón canónico documentado y no contiene guiones de borde ni consecutivos.
- Completado: no se implementan estrategias de unicidad, persistencia ni transliteración general fuera de alcance.

**Límite de fase:** no existe todavía un punto de entrada de línea de comandos ni pruebas de integración de procesos; ambos pertenecen a las Fases 4 y 5.

## Fase 4 — Adaptador de línea de comandos — Completada, P0

**Objetivo:** conectar la entrada de terminal con el núcleo sin duplicar reglas de dominio.

**Entregables completados:**

- Punto de entrada [src/cli.ts](src/cli.ts), publicado como binario local `slug-generator` mediante [package.json](package.json).
- Interpretación estricta de un único argumento posicional, ayuda aislada `--help`/`-h` y errores de uso definidos por el contrato.
- Delegación exclusiva de la normalización a [src/slug.ts](src/slug.ts), sin añadir reglas de transformación, red, persistencia, configuración ni interacción.
- Salida correcta y ayuda por salida estándar; diagnósticos por salida de error; códigos `0`, `1` y `2` conforme al contrato.
- Pruebas de proceso en [tests/cli.test.mjs](tests/cli.test.mjs) que verifican argumentos, UTF-8, ayuda, canales, errores y códigos de salida.

**Verificaciones ejecutadas:**

- `npm test`: compilación aprobada y 46 pruebas superadas, sin fallos, incluidas las de la CLI.

**Dependencias:** Fase 3.

**Criterios de finalización verificables:**

- Completado: la invocación del binario compilado produce un slug correcto con una sola línea de salida estándar.
- Completado: las entradas inválidas no devuelven slug, escriben únicamente el diagnóstico estable en salida de error y devuelven el código aplicable.
- Completado: el adaptador delega la normalización en el núcleo y se mantiene como capa de proceso fina.
- Completado: la ayuda coincide con el texto estable del contrato, no usa color ni interacción y explica el argumento y ejemplo requeridos.

## Fase 5 — Validaciones y pruebas automatizadas — Completada, P0

**Objetivo:** demostrar comportamiento, estabilidad del contrato y aislamiento local.

**Entregables completados:**

- Ampliación de [tests/slug.test.mjs](tests/slug.test.mjs) con normalización Unicode en forma descompuesta, mayúsculas, dígitos, separadores repetidos y de borde, símbolos, alfabetos no latinos y tabla latina mínima.
- Validación estable de entrada ausente, nula, no textual, vacía, formada solo por espacios Unicode o sin contenido normalizable.
- Regresiones para patrón canónico, ausencia de guiones consecutivos o de borde, determinismo e idempotencia de cada salida válida.
- Ampliación de [tests/cli.test.mjs](tests/cli.test.mjs), que ejecuta el binario compilado y comprueba casos válidos UTF-8, ayuda, ausencia y exceso de argumentos, opciones desconocidas, diagnósticos de dominio, canales y códigos `0`, `1` y `2`.
- No se añadieron fixtures ni dependencias: las tablas de datos textuales son deterministas, no sensibles e independientes de sistema operativo, zona horaria o configuración regional.

**Verificaciones ejecutadas:**

- `npm test`: compilación aprobada y 49 pruebas superadas, sin fallos.

**Dependencias:** Fases 2, 3 y 4.

**Criterios de finalización verificables:**

- Completado: la suite cubre todos los escenarios normativos `N-*`, `L-*`, `S-*`, `U-*`, `E-*` y `C-*` aplicables de [docs/ESCENARIOS_FASE_1.md](docs/ESCENARIOS_FASE_1.md).
- Completado: se comprueba explícitamente la separación de canales de salida y los códigos de error de la CLI.
- Completado: la regresión confirma determinismo, idempotencia, el alfabeto restringido y la ausencia de guiones no canónicos.
- Completado: las pruebas no requieren red, secretos, datos personales ni servicios de terceros.

## Fase 6 — Documentación de uso, calidad y entrega — Completada, P0

**Objetivo:** publicar una entrega local comprensible, verificable y compatible con el SOP diario.

**Entregables completados:**

- [README.md](README.md) actualizado con el estado final de la versión 1, enlace a la guía reproducible y estrategia de pruebas ya ejecutada.
- [docs/USO_LOCAL.md](docs/USO_LOCAL.md) añadido con requisitos, instalación limpia, compilación, invocación, ayuda, canales, códigos y comandos de calidad reales.
- [assets/DEMO_15S.md](assets/DEMO_15S.md) añadido como guion local breve que muestra entradas válidas, salida normalizada y un error controlado sin datos sensibles.
- Scripts de formato de [package.json](package.json) ampliados para cubrir la documentación Markdown y la demostración.
- Revisión de enlaces, alcance, dependencias, secretos y artefactos generados; no se añadió funcionalidad, integración externa ni dato sensible.

**Verificaciones ejecutadas:**

- `npm ci`: instalación limpia aprobada, sin vulnerabilidades notificadas.
- `npm run format`, `npm run quality`, `npm run build` y `npm test`: aprobados; la suite completa supera 49 pruebas.
- Invocaciones locales de la CLI para un caso válido, ayuda y errores de uso y contenido: canales y códigos coherentes con [docs/CONTRATO_V1.md](docs/CONTRATO_V1.md).
- `git diff --check`, `git status --short --ignored` y `git check-ignore`: revisión de diferencias y confirmación de que `dist/` y `node_modules/` permanecen ignorados.

**Dependencias:** Fases 1 a 5.

**Criterios de finalización verificables:**

- Completado: una persona puede instalar, invocar y comprobar el proyecto siguiendo documentación en español.
- Completado: la demostración muestra entrada, acción y resultado sin información sensible.
- Completado: la documentación refleja únicamente comportamiento y verificaciones existentes.
- Completado: la revisión final confirma que el proyecto mantiene el alcance atómico, local y sin estado.

## Criterio de salida de la versión 1

La versión 1 estará lista cuando las Fases 1 a 6 estén completadas, exista una CLI TypeScript local reproducible, el núcleo esté validado de forma automatizada, la integración de terminal esté comprobada, la documentación sea coherente y no se haya incorporado funcionalidad fuera de alcance.

## Trabajo completado en esta tarea

Las Fases 0 a 6 están completadas y cierran la versión 1. El proyecto dispone de configuración TypeScript reproducible, núcleo de normalización puro, CLI compilable, binario local, formato, comprobación de tipos, pruebas unitarias y de proceso, guía de uso y demostración local breve.
