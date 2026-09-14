# Día 14 — Validador de configuración

> Microproyecto CLI del reto [30 Días, 30 Proyectos](../../README.md). **Estado:** versión 1 completada y verificada localmente.

## Propósito

Validar de manera local y determinista un archivo `.env` proporcionado explícitamente contra un esquema JSON declarativo definido por la persona usuaria. La herramienta detecta configuración incompleta, incompatible o contradictoria antes de ejecutar una aplicación o una tarea de automatización.

El proyecto está diseñado para uso local y automatización de CI: recibirá las rutas del archivo `.env` y del esquema, aplicará reglas seguras y devolverá un resumen JSON apto para procesos. Los valores marcados como secretos no se expondrán en resultados, diagnósticos, pruebas ni recursos de demostración.

## Alcance previsto de la versión 1

- Ofrecer una CLI TypeScript local respaldada por Zod.
- Leer un archivo `.env` y un esquema JSON desde rutas posicionales explícitas.
- Validar un formato propio, limitado y versionado de esquema JSON; no interpretar JSON Schema completo.
- Admitir variables de tipo texto, número, booleano, enumeración, URL y lista codificada como JSON.
- Admitir valores obligatorios u opcionales, valores por defecto y restricciones compatibles con cada tipo.
- Admitir patrones RegExp declarados, después de que el esquema los haya validado.
- Aplicar solo transformaciones declarativas internas y cerradas: recorte, cambio de mayúsculas/minúsculas, división controlada y parseo JSON. No se admitirán expresiones JavaScript, comandos, imports ni plugins.
- Comprobar dependencias globales entre claves mediante reglas `allOrNone`, `requires` y `forbids`.
- Informar claves válidas, inválidas, valores por defecto aplicados y advertencias sin revelar valores secretos.
- Emitir un único resumen JSON por salida estándar en éxito, o un único error JSON estructurado por salida de error en fallo.
- Incluir pruebas unitarias, integración de CLI, fixtures sintéticos y documentación reproducible antes de declarar completada la versión 1.

## Fuera de alcance

- Cargar o fusionar `process.env`, múltiples archivos `.env` o cadenas implícitas de precedencia.
- Modificar, reescribir o crear archivos `.env`.
- Interpolación de variables, expansión de shell, sustitución de comandos o evaluación de código en valores o esquemas.
- Gestores de secretos, cifrado, servicios cloud, red, persistencia, telemetría o cuentas externas.
- Compatibilidad general con JSON Schema, YAML, TOML, esquemas anidados o tipos de objeto arbitrarios.
- Transformaciones definidas por la persona usuaria, módulos dinámicos, callbacks o expresiones ejecutables.
- Interfaz web, API HTTP, modo interactivo o corrección automática de configuraciones inválidas.

## Tecnología y restricciones

El índice raíz asigna al día 14 la categoría **Configuración** y el stack **TypeScript, Zod** en [README.md](../../README.md). La Fase 1 cierra el comportamiento público y la Fase 2 fija el entorno aislado descrito en [`package.json`](package.json): Node.js `>=22.0.0`, npm `>=10.0.0`, TypeScript `5.8.2`, Zod `3.24.2`, dotenv `16.4.7`, `@types/node` `22.14.1` y Prettier `3.5.3`.

Zod valida y compila en la Fase 3 la gramática cerrada del esquema mediante [`src/schema.ts`](src/schema.ts). El compilador no realiza E/S: recibe JSON ya cargado o texto JSON, devuelve un plan inmutable y seguro para el futuro motor puro, y separa JSON malformado de las incoherencias declarativas mediante [`src/errors.ts`](src/errors.ts). dotenv es el parser de `.env` seleccionado para la Fase 5; su uso estará restringido por las reglas observables de [docs/CONTRATO_V1.md](docs/CONTRATO_V1.md), por lo que no habilita interpolación, expansión de shell ni sintaxis adicional. Las pruebas emplean el runner nativo `node --test`, sin una dependencia adicional.

No se contempla una integración externa para la versión 1. La ruta principal y el fallback son locales: los archivos de entrada explícitos y fixtures sintéticos permiten demostrar el comportamiento sin secretos, credenciales, red ni proveedor externo, conforme a [docs/DAILY_WORKFLOW.md](../../docs/DAILY_WORKFLOW.md).

### Instalación, ejecución y comprobaciones

Desde este directorio, una instalación limpia se prepara con `npm ci`. Compila y ejecuta la CLI usando únicamente rutas explícitas:

```text
npm run build
node ./dist/cli.js ./data/fixtures/valid-configuration.env ./data/fixtures/valid-schema.json
```

Los comandos disponibles comprueban el entorno y las suites de compilación del esquema, el motor puro, la CLI y las regresiones con fixtures sintéticos:

```text
npm run build
npm run typecheck
npm run format:check
npm test
npm run quality
```

La Fase 4 proporciona [`validateConfiguration()`](src/validator.ts:89), un motor sin E/S que recibe un plan compilado y un mapa `.env` ya parseado. La Fase 5 añade [`src/cli.ts`](src/cli.ts), que lee exclusivamente las dos rutas explícitas, encapsula el parser `.env`, delega al compilador y al motor, y emite una única respuesta por canal. La guía completa, la solución de problemas y la demostración sintética están en [`docs/USO_LOCAL.md`](docs/USO_LOCAL.md) y [`assets/DEMO_15S.md`](assets/DEMO_15S.md).

## Interfaz de línea de comandos contratada

La interfaz, sus canales y códigos están cerrados en [docs/CONTRATO_V1.md](docs/CONTRATO_V1.md). Su forma es:

```text
env-config-validator <ruta-env> <ruta-schema>
```

- Se exigen exactamente dos rutas posicionales: una al archivo `.env` y otra al esquema JSON.
- La ayuda aislada está disponible mediante `--help` y `-h`.
- La salida correcta es JSON en salida estándar; los errores se emiten como JSON en salida de error.
- La herramienta no descubre archivos automáticamente ni consulta variables de entorno del proceso.
- Los códigos de salida son `0` para éxito o ayuda, `2` para uso, `3` para entrada, `4` para esquema, `5` para configuración y `1` para un fallo interno seguro.
- El detalle normativo de las envolturas JSON, mensajes principales, incidencias y redacción está en [docs/CONTRATO_V1.md](docs/CONTRATO_V1.md).

## Modelo de validación contratado

El esquema describe variables y reglas globales de dependencia. Cada variable podrá declarar, según corresponda, tipo, opcionalidad, secreto, valor por defecto, transformaciones internas, restricciones y metadatos seguros de diagnóstico.

La v1 cierra la diferencia entre ausencia y vacío, la aplicación de valores por defecto, el orden de transformaciones, la conversión de tipo, las restricciones, las claves no declaradas y las dependencias. El pipeline normativo y la gramática completa del esquema constan en [docs/CONTRATO_V1.md](docs/CONTRATO_V1.md); los casos que guiarán pruebas futuras constan en [docs/ESCENARIOS_FASE_1.md](docs/ESCENARIOS_FASE_1.md).

## Seguridad y privacidad

- Los archivos `.env` pueden contener datos sensibles y se tratarán únicamente como entrada local.
- Las variables declaradas como secretas no deberán aparecer con su valor en resultados, errores, fixtures, snapshots, documentación ni demostraciones.
- Un esquema no podrá ejecutar código ni solicitar recursos externos.
- Los diagnósticos evitarán trazas internas, contenido completo de archivos y detalles innecesarios del sistema anfitrión.
- La guía y la demostración emplean exclusivamente valores ficticios y nunca muestran contenido de `.env`.

## Estrategia de pruebas contratada

1. Pruebas unitarias de validación del esquema, compilación de reglas, transformaciones, tipos, restricciones y dependencias.
2. Pruebas con fixtures sintéticos `.env` y JSON para resultados correctos, advertencias, valores por defecto, errores de esquema y errores de configuración.
3. Pruebas de integración de procesos para argumentos, ayuda, JSON por canal correcto, códigos de salida y lectura de archivos.
4. Regresiones de determinismo, orden estable de incidencias y ausencia de filtraciones de secretos en cualquier salida pública.
5. Comprobaciones de tipos, formato, compilación e instalación limpia antes de la entrega.

## Criterios de aceptación de la versión 1

La primera versión estará aceptada cuando:

- Una instalación documentada permita ejecutar la CLI contra rutas explícitas y fixtures sintéticos.
- El esquema soporte únicamente las construcciones declaradas por el contrato y rechace las desconocidas o incompatibles.
- Las reglas de tipo, transformación, restricciones y dependencias produzcan resultados deterministas.
- Los errores de uso, entrada, esquema y configuración estén separados mediante JSON estructurado, canales de salida y códigos de proceso estables.
- Ninguna salida pública revele valores de variables secretas.
- Existan pruebas unitarias y de CLI reproducibles, sin red, proveedores ni secretos reales.
- README, contrato, roadmap, ayuda y demostración describan el mismo comportamiento implementado.

## Estructura prevista

```text
projects/day-14-env-config-validator/
├── README.md
├── ROADMAP.md
├── docs/
├── src/
├── tests/
├── data/
│   ├── fixtures/
│   └── expected/
└── assets/
```

| Ruta                                                   | Responsabilidad prevista                                                                     |
| ------------------------------------------------------ | -------------------------------------------------------------------------------------------- |
| [README.md](README.md)                                 | Alcance, límites, guía de inicio y estado verificable.                                       |
| [ROADMAP.md](ROADMAP.md)                               | Fases, prioridades, dependencias, riesgos y aceptación.                                      |
| [docs/CONTRATO_V1.md](docs/CONTRATO_V1.md)             | Fuente de verdad de la CLI, los archivos, esquema, resultados, errores y seguridad v1.       |
| [docs/ESCENARIOS_FASE_1.md](docs/ESCENARIOS_FASE_1.md) | Vectores documentales trazables para la implementación y pruebas.                            |
| [docs/DECISIONES.md](docs/DECISIONES.md)               | Registro de decisiones de alcance, seguridad y semántica no fijadas por el índice raíz.      |
| [docs/USO_LOCAL.md](docs/USO_LOCAL.md)                 | Instalación limpia, uso, códigos, comprobaciones y solución de problemas local.              |
| [src](src)                                             | Código TypeScript: errores de dominio, compilador de esquema, motor puro y adaptador de CLI. |
| [tests](tests)                                         | Pruebas de compilación, motor puro, CLI y regresiones con fixtures.                          |
| [data/fixtures](data/fixtures)                         | Entradas sintéticas `.env` y esquemas JSON de regresión, sin datos reales.                   |
| [data/expected](data/expected)                         | Respuestas públicas esperadas, parseables y siempre redacted.                                |
| [assets/DEMO_15S.md](assets/DEMO_15S.md)               | Guion reproducible de 15 segundos con datos sintéticos y sin exposición de secretos.         |

## Estado de esta entrega

Las Fases 0 a 7 están completadas. La versión 1 incluye contrato cerrado, entorno npm reproducible, compilador Zod, motor puro determinista, adaptador CLI UTF-8, salidas JSON redacted, pruebas unitarias y de proceso con fixtures sintéticos, guía local y demo segura. La revisión final confirma una herramienta local, atómica y sin estado, sin red, servicios externos ni consulta implícita de `process.env`. La instalación, uso y resolución de problemas están en [`docs/USO_LOCAL.md`](docs/USO_LOCAL.md); el guion de publicación está en [`assets/DEMO_15S.md`](assets/DEMO_15S.md); las fases y condiciones de salida residen en [ROADMAP.md](ROADMAP.md).
