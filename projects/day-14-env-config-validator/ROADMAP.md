# Roadmap — Validador de configuración

Este roadmap organiza el desarrollo del proyecto 14 como una CLI TypeScript local que valida un archivo `.env` explícito frente a un esquema JSON declarativo y seguro. Las **Fases 0, 1, 2, 3 y 4** están completadas: reservan estructura, cierran el contrato, preparan un entorno reproducible, compilan el esquema y validan mapas de configuración ya parseados sin E/S.

## Objetivo de la versión 1

Entregar una CLI que reciba la ruta de un archivo `.env` y la ruta de un esquema JSON, valide ambos de manera determinista y comunique un resumen JSON seguro. Las variables marcadas como secretas nunca aparecerán con su valor en la salida pública.

La primera versión soportará variables de texto, número, booleano, enumeración, URL y listas JSON; valores obligatorios, opcionales y por defecto; patrones; transformaciones internas cerradas; y dependencias `allOrNone`, `requires` y `forbids`.

## Prioridad y límites

**Prioridad P0:** validación local de una configuración explícita, contrato de esquema acotado, redacción de secretos, resultados JSON estables y pruebas reproducibles.

**Fuera de P0:** `process.env`, múltiples fuentes y precedencias, escritura de `.env`, interpolación, ejecución de comandos o JavaScript, plugins, JSON Schema general, YAML/TOML, objetos anidados, API, interfaz gráfica, persistencia, cloud, telemetría y secretos reales.

## Estado de las fases

- [x] **Fase 0 — Preparación documental y estructural:** completada.
- [x] **Fase 1 — Contrato público, esquema y modelo de seguridad:** completada documentalmente.
- [x] **Fase 2 — Entorno TypeScript y calidad:** completada.
- [x] **Fase 3 — Validación y compilación del esquema:** completada.
- [x] **Fase 4 — Motor puro de validación de configuración:** completada.
- [x] **Fase 5 — Adaptador de CLI y archivos:** completada.
- [x] **Fase 6 — Pruebas automatizadas y regresión:** completada.
- [x] **Fase 7 — Guía de uso, demostración y entrega:** completada.

## Dependencias entre fases

```text
Fase 0 → Fase 1 → Fase 2 → Fase 3 → Fase 4 → Fase 5 → Fase 6 → Fase 7
                              │                  │
                              └──────────────────┴── pruebas unitarias y de proceso
```

- La Fase 1 es la fuente de verdad para sintaxis, semántica, errores y seguridad de las fases posteriores.
- La Fase 2 habilita instalación, compilación y comprobaciones, sin sustituir las pruebas funcionales.
- La Fase 3 valida el documento de esquema y prepara un plan interno seguro antes de procesar configuraciones.
- La Fase 4 depende del esquema compilado y no realizará lectura de archivos ni salida de terminal.
- La Fase 5 conecta rutas, archivos, motor y contrato de proceso sin duplicar reglas de dominio.
- La Fase 6 demuestra el contrato del núcleo y de la CLI una vez ambas capas existan.
- La Fase 7 requiere que la ruta P0 esté verificada y documentada.

## Fase 0 — Preparación documental y estructural — Completada

**Objetivo:** crear la ubicación oficial del proyecto y fijar un alcance entregable sin adelantar código ni configuración funcional.

**Entregables:**

- Directorio [projects/day-14-env-config-validator](.) alineado con el enlace del índice raíz.
- [README.md](README.md) en español con propósito, alcance, exclusiones, seguridad, estructura y aceptación prevista.
- Este roadmap con secuencia, dependencias, riesgos y criterios de salida.
- Directorios reservados [docs](docs), [src](src), [tests](tests), [data/fixtures](data/fixtures), [data/expected](data/expected) y [assets](assets).

**Dependencias:** ninguna.

**Criterios de aceptación:**

- La ubicación coincide con [README.md](../../README.md) del repositorio.
- La documentación identifica TypeScript y Zod como stack asignado y distingue lo confirmado de lo pendiente.
- No se han creado módulos ejecutables, manifiesto npm, dependencia, prueba automática, fixture con datos, configuración funcional ni secreto.
- La estructura anticipa las convenciones de [README.md](../../README.md) y [docs/DAILY_WORKFLOW.md](../../docs/DAILY_WORKFLOW.md).

## Fase 1 — Contrato público, esquema y modelo de seguridad — P0

**Objetivo:** cerrar una especificación sin ambigüedad para poder implementar y probar sin inventar comportamiento.

**Tareas:**

- Crear [docs/CONTRATO_V1.md](docs/CONTRATO_V1.md) como fuente de verdad de la CLI, las entradas, salidas, errores y códigos de proceso.
- Definir el documento raíz del esquema, su versión, las variables, las dependencias y la política de claves no declaradas.
- Cerrar tipos admitidos, restricciones compatibles, listas JSON, patrones y valores por defecto.
- Cerrar semántica de ausente frente a vacío, orden de transformaciones, conversión de tipo y validación de dependencias.
- Restringir transformaciones a operaciones internas declarativas: `trim`, cambios de caso, separación controlada y parseo JSON; prohibir expresiones, comandos, imports y plugins.
- Establecer la semántica de `allOrNone`, `requires` y `forbids`, incluidos conflictos entre reglas.
- Definir el modelo de secretos y los campos que están prohibidos en resultados públicos.
- Especificar los escenarios en [docs/ESCENARIOS_FASE_1.md](docs/ESCENARIOS_FASE_1.md) y registrar las decisiones en [docs/DECISIONES.md](docs/DECISIONES.md).

**Dependencias:** Fase 0.

**Entregables completados:**

- [docs/CONTRATO_V1.md](docs/CONTRATO_V1.md) como fuente de verdad de argumentos, codificación, archivos, esquema, tipos, transformaciones, resultados, errores, códigos de proceso y redacción.
- [docs/ESCENARIOS_FASE_1.md](docs/ESCENARIOS_FASE_1.md) con vectores documentales de CLI, presencia, tipos, listas, patrones, claves no declaradas, dependencias y secretos.
- [docs/DECISIONES.md](docs/DECISIONES.md) con las decisiones locales de alcance, parser, seguridad y semántica no definidas por el índice raíz.
- [README.md](README.md) actualizado para diferenciar el contrato cerrado del código y entorno que siguen pendientes.

**Criterios de aceptación:**

- Completado: cada caso de uso válido e inválido tiene una salida o error JSON inequívoco.
- Completado: el contrato asigna códigos separados para uso, lectura o parseo, esquema y configuración inválida.
- Completado: se documentan la semántica contractual del parser `.env`, la codificación UTF-8 y las construcciones no admitidas; la dependencia concreta se seleccionará en Fase 2.
- Completado: el contrato prohíbe toda forma de ejecución de código aportado por el esquema.
- Completado: los escenarios incluyen ausencia, vacío, defecto, secreto, lista, patrón, transformación, clave no declarada y cada dependencia.

**Límite de fase:** no se han creado la CLI, el manifiesto npm, configuración TypeScript, dependencia de parser, Zod, módulos, fixtures ejecutables ni pruebas automatizadas. Estos elementos continúan explícitamente en las Fases 2 a 6.

## Fase 2 — Entorno TypeScript y calidad — Completada, P0

**Objetivo:** crear una base mínima, aislada y reproducible para compilar, ejecutar y comprobar el proyecto.

**Entregables completados:**

- [package.json](package.json), [package-lock.json](package-lock.json), [tsconfig.json](tsconfig.json) y [`.prettierrc.json`](.prettierrc.json) aislados dentro del proyecto.
- Requisitos de motor: Node.js `>=22.0.0` y npm `>=10.0.0`, coherentes con la CLI TypeScript reciente de [day-13-url-slug-generator](../day-13-url-slug-generator/package.json).
- Dependencias de producción exactas: Zod `3.24.2` para el esquema de Fase 3 y dotenv `16.4.7` como parser que la Fase 5 encapsulará conforme a [docs/CONTRATO_V1.md](docs/CONTRATO_V1.md).
- Dependencias de desarrollo exactas: TypeScript `5.8.2`, `@types/node` `22.14.1` y Prettier `3.5.3`.
- Scripts `build`, `typecheck`, `test`, `format`, `format:check` y `quality`; el runner previsto para las pruebas posteriores es `node --test`.
- Punto de anclaje tipado [src/environment.d.ts](src/environment.d.ts), sin lógica de dominio ni adaptación de CLI.
- No se añade [`.gitignore`](.gitignore) local: el [`.gitignore`](../../.gitignore) raíz ya excluye `node_modules/`, `dist/`, `*.tsbuildinfo` y logs de npm.

**Dependencias:** Fase 1.

**Criterios de aceptación:**

- Completado: `npm ci` prepara el entorno sin secretos, cuentas ni configuración adicional.
- Completado: los comandos de build, typecheck y formato funcionan sobre la estructura mínima.
- Completado: versiones y dependencias están documentadas, bloqueadas y aisladas en el proyecto.
- Completado: no existe red, proveedor ni variable de entorno requerida por el entorno de ejecución futuro.

**Límite de fase:** Zod y dotenv están instalados pero no se invocan todavía. La validación del esquema, tipos, valores por defecto, transformaciones —incluidos `splitComma` y `parseJson`—, lectura de archivos, CLI y pruebas de comportamiento pertenecen a las Fases 3 a 6.

## Fase 3 — Validación y compilación del esquema — Completada, P0

**Objetivo:** validar el esquema JSON y convertirlo en un plan interno seguro antes de evaluar cualquier `.env`.

**Tareas:**

- Modelar con Zod el documento de esquema, variables, transformaciones, restricciones y dependencias.
- Rechazar campos de esquema desconocidos, versiones no soportadas, reglas incompatibles, duplicados y patrones malformados conforme al contrato.
- Validar la compatibilidad entre tipo, restricciones, transformaciones y valor por defecto.
- Compilar un plan de validación inmutable y separado de entrada/salida.
- Diseñar errores de dominio serializables que distingan documento JSON malformado, esquema inválido y configuración inválida.

**Entregables completados:**

- [`src/schema.ts`](src/schema.ts) modela con Zod el documento raíz, variables, restricciones, transformaciones y dependencias cerradas de v1.
- [`src/errors.ts`](src/errors.ts) define errores de dominio seguros, códigos estables e incidencias con ruta declarativa.
- El compilador valida nombres, campos desconocidos, límites, patrones, transformaciones, valores por defecto, protocolos y dependencias, y devuelve un plan sin E/S con colecciones inmutables.
- [`tests/schema.test.mjs`](tests/schema.test.mjs) cubre esquemas válidos, JSON malformado, campos desconocidos, defaults, transformaciones, patrones y dependencias inválidas.

**Límite de fase:** no interpreta archivos `.env`, no convierte valores de configuración y no implementa CLI ni salida de proceso; esas responsabilidades permanecen en las Fases 4 y 5.

**Dependencias:** Fases 1 y 2.

**Criterios de aceptación:**

- Los esquemas inválidos fallan antes de procesar valores de configuración.
- El modelo no permite expresiones, rutas de módulos, callbacks, comandos ni comportamiento dinámico.
- Todas las incoherencias se informan mediante códigos y rutas estables del esquema.
- Un esquema válido genera un plan consumible por el núcleo sin acceso a archivos ni terminal.

## Fase 4 — Motor puro de validación de configuración — Completada, P0

**Objetivo:** evaluar datos `.env` ya parseados contra el plan de esquema de forma local, determinista y sin efectos secundarios.

**Tareas:**

- Adaptar el resultado del parser `.env` a un mapa de valores brutos conservando la distinción entre clave ausente y valor vacío.
- Resolver valores por defecto según el orden normativo.
- Aplicar únicamente transformaciones declarativas admitidas.
- Convertir valores a sus tipos, validar restricciones y listas JSON.
- Evaluar la política de claves no declaradas y las dependencias globales.
- Construir un resumen público redacted con claves, estados, advertencias, valores por defecto aplicados e incidencias ordenadas.

**Entregables completados:** motor TypeScript puro en [`src/validator.ts`](src/validator.ts) que evalúa mapas ya parseados, distingue ausencia de vacío, resuelve valores por defecto, aplica el pipeline de tipos/restricciones, procesa claves no declaradas y dependencias, y genera resultados públicos redacted y ordenados. La regresión del motor está en [`tests/validator.test.mjs`](tests/validator.test.mjs).

**Límite de fase:** no lee archivos `.env`, no analiza argumentos ni escribe en `stdout`/`stderr`; esas responsabilidades quedan para el adaptador de la Fase 5.

**Dependencias:** Fase 3.

**Criterios de aceptación:**

- La misma entrada y el mismo esquema generan el mismo resultado y el mismo orden de incidencias.
- Se comprueban todos los tipos, restricciones, transformaciones y dependencias cerrados en la Fase 1.
- Los valores secretos, incluidos valores por defecto transformados, no aparecen en el resultado público.
- El motor no lee ni escribe archivos, no usa red, no modifica procesos ni depende de estado global.

## Fase 5 — Adaptador de CLI y archivos — Completada, P0

**Objetivo:** exponer el motor mediante una CLI que respete el contrato de rutas, canales JSON y códigos de proceso.

**Tareas:**

- Añadir el binario local y el punto de entrada TypeScript.
- Interpretar exactamente dos rutas posicionales y ayuda aislada.
- Leer ambos archivos con UTF-8 explícito y traducir errores de filesystem o parseo al sobre público correspondiente.
- Delegar validación de esquema y configuración al núcleo sin duplicar lógica.
- Emitir una sola respuesta JSON por salida estándar en éxito o una sola respuesta JSON por salida de error en fallo.
- Aplicar los códigos de proceso documentados y evitar trazas o valores secretos.

**Entregables completados:**

- [`src/cli.ts`](src/cli.ts) implementa el binario local declarado en [`package.json`](package.json), interpreta la ayuda y las dos rutas explícitas, y no consulta `process.env`.
- El adaptador lee archivos regulares como UTF-8, elimina BOM UTF-8 opcional, encapsula `dotenv` y convierte fallos de entrada, esquema, configuración e internos en envoltorios públicos seguros.
- [`tests/cli.test.mjs`](tests/cli.test.mjs) cubre ayuda, éxito, canales, códigos, argumentos, opciones, entradas, esquema, configuración y redacción de un secreto sintético.

**Límite de fase:** no añade fixtures persistentes, matriz completa de regresión ni guía de uso; esos entregables continúan en las Fases 6 y 7.

**Dependencias:** Fases 2 y 4.

**Criterios de aceptación:**

- Una ejecución válida devuelve solo JSON válido por stdout y el código de éxito.
- Los fallos de uso, archivos, esquema y configuración usan stderr y sus códigos diferenciados.
- No se mezclan diagnósticos con la respuesta correcta.
- La CLI no descubre archivos ni consulta implícitamente `process.env`.

## Fase 6 — Pruebas automatizadas y regresión — Completada, P0

**Objetivo:** demostrar el contrato, la seguridad de salida y la reproducibilidad de la solución.

**Tareas:**

- Crear pruebas unitarias para esquema, plan, transformaciones, conversión de tipos, restricciones, dependencias y redacción.
- Añadir fixtures sintéticos `.env` y JSON, junto con resultados esperados sin secretos.
- Crear pruebas de proceso para argumentos, ayuda, archivos ausentes, JSON malformado, esquema inválido, configuración inválida, canales y códigos.
- Añadir regresiones de determinismo, orden estable y ausencia de valores secretos en cualquier salida pública.
- Ejecutar build, typecheck, formato y pruebas desde una instalación limpia.

**Entregables completados:**

- Los tests unitarios de [`tests/schema.test.mjs`](tests/schema.test.mjs) y [`tests/validator.test.mjs`](tests/validator.test.mjs) cubren la compilación, transformaciones, conversiones, restricciones, dependencias, orden y redacción.
- Los fixtures sintéticos de [`data/fixtures`](data/fixtures) y resultados redacted de [`data/expected`](data/expected) ejercitan configuraciones correctas e inválidas sin conservar el valor del secreto sintético en ninguna respuesta esperada.
- [`tests/cli.test.mjs`](tests/cli.test.mjs) y [`tests/regression.test.mjs`](tests/regression.test.mjs) comprueban argumentos, ayuda, archivos ausentes/no regulares/no UTF-8, `.env`, JSON y esquema inválidos, canales, códigos, resultados parseables, determinismo y ausencia de filtraciones.

**Dependencias:** Fases 3, 4 y 5.

**Criterios de aceptación:**

- Los escenarios de la Fase 1 se trazan a pruebas automáticas.
- Todas las salidas de éxito y fallo pueden parsearse como JSON y respetan el contrato de canal.
- Las pruebas prueban que valores secretos sintéticos no aparecen en stdout, stderr, fixtures esperados ni documentación de demo.
- La suite no depende de red, credenciales, tiempo, zona horaria, configuración regional ni variables de entorno de la máquina.

## Fase 7 — Guía de uso, demostración y entrega — Completada, P0

**Objetivo:** entregar una versión 1 comprensible, demostrable y segura para publicación.

**Tareas:**

- Actualizar [README.md](README.md) con comandos reales, interfaz final, errores, estructura, límites y estado de verificación.
- Añadir [docs/USO_LOCAL.md](docs/USO_LOCAL.md) con instalación limpia, uso, comprobaciones y solución de problemas.
- Crear [assets/DEMO_15S.md](assets/DEMO_15S.md) con un guion local que muestre una validación correcta y un fallo seguro usando datos ficticios.
- Revisar enlaces, sincronía entre contrato/roadmap/README/ayuda, dependencias, artefactos y secretos.
- Confirmar que el proyecto satisface el proceso de entrega de [docs/DAILY_WORKFLOW.md](../../docs/DAILY_WORKFLOW.md).

**Entregables completados:**

- [`README.md`](README.md) describe la instalación, ejecución, interfaz final, límites, seguridad, estructura y estado verificable de v1.
- [`docs/USO_LOCAL.md`](docs/USO_LOCAL.md) permite instalar desde cero, ejecutar fixtures sintéticos, interpretar canales y códigos, comprobar calidad y resolver fallos comunes sin servicios externos.
- [`assets/DEMO_15S.md`](assets/DEMO_15S.md) aporta un guion local de 15 segundos con validación correcta y error seguro, sin mostrar contenido ni valores de `.env`.
- La revisión de entrega mantiene enlaces locales, scripts, dependencias, fixtures, contrato y demo coherentes; `dist` y `node_modules` permanecen fuera de control de versiones.

**Dependencias:** Fases 1 a 6.

**Criterios de aceptación:**

- Una persona puede instalar, ejecutar y verificar el proyecto únicamente siguiendo documentación local.
- La demostración utiliza valores ficticios y no revela ningún valor que el esquema marque como secreto.
- La documentación describe solo comportamiento existente y comprobado.
- La revisión final confirma que la herramienta sigue siendo local, atómica, sin estado y sin integración externa.

## Riesgos y mitigaciones

| Riesgo                                               | Mitigación prevista                                                                                           |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Filtración de secretos en diagnósticos o regresiones | Modelo público redacted, datos sintéticos y pruebas explícitas de no filtración.                              |
| El esquema se convierte en vector de ejecución       | Gramática JSON cerrada; transformaciones enumeradas; prohibición de expresiones, comandos, imports y plugins. |
| Complejidad excesiva para un microproyecto           | Prioridad estricta: contrato, motor puro, redacción y CLI antes de extensiones posteriores.                   |
| Ambigüedad del formato `.env`                        | Seleccionar un parser y documentar su semántica exacta en el contrato.                                        |
| Patrones RegExp problemáticos                        | Validar sintaxis, limitar construcción permitida y documentar riesgo residual antes de aceptar el contrato.   |
| Resultados no deterministas                          | Ordenar claves e incidencias; no heredar `process.env`; no depender de hora, locale o zona horaria.           |
| Conflicto entre dependencias                         | Detectar y rechazar combinaciones incompatibles durante la validación del esquema.                            |

## Criterio de salida de la versión 1

La versión 1 estará lista cuando las Fases 1 a 7 estén aceptadas: existirá una CLI TypeScript local instalable, un formato de esquema JSON documentado y acotado, un motor puro validado, resultados JSON seguros, errores y códigos estables, pruebas reproducibles, una demo sintética y documentación coherente.
