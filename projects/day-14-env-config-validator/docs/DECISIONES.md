# Decisiones de alcance — Validador de configuración

Este documento registra las decisiones necesarias para concretar el proyecto 14. El índice raíz solo asigna **Validador de configuración**, categoría **Configuración** y tecnologías **TypeScript, Zod**; el resto de decisiones de producto y seguridad se fijan para la versión 1 local. Cualquier cambio posterior deberá actualizar [README.md](../README.md), [ROADMAP.md](../ROADMAP.md), [CONTRATO_V1.md](CONTRATO_V1.md) y los escenarios afectados.

## D-01 — Dos archivos explícitos y ninguna fuente implícita

**Decisión:** la CLI v1 acepta exactamente una ruta `.env` y una ruta de esquema JSON como argumentos posicionales. No consulta `process.env`, no descubre archivos por directorio actual y no mezcla fuentes.

**Motivo:** elimina precedencias ambiguas, evita que el entorno de la máquina altere resultados y permite una ejecución determinista en CI y local.

**Consecuencia:** la ausencia, exceso o combinación incorrecta de argumentos produce error de uso con código `2`. Capas como `.env.local`, variables de proceso o precedencia por entorno quedan aplazadas.

## D-02 — Formato de esquema propio, pequeño y versionado

**Decisión:** el esquema usa un objeto JSON estricto con `version: "v1"`, `variables`, `unknownKeys` y `dependencies`. No es JSON Schema ni admite claves no definidas.

**Motivo:** Zod podrá validar una gramática acotada y predecible sin prometer compatibilidad parcial con una especificación mucho más amplia.

**Consecuencia:** una clave, versión, restricción o combinación no documentada causa un error de esquema. Compatibilidad con JSON Schema, YAML, TOML, objetos anidados y referencias externas queda fuera de V1.

## D-03 — Transformaciones declarativas y sin ejecución

**Decisión:** las únicas transformaciones son `trim`, `lowercase`, `uppercase`, `splitComma` y `parseJson`, con reglas cerradas por tipo y orden explícito en el esquema.

**Motivo:** un esquema proporcionado por usuario no debe convertirse en vector para evaluar JavaScript, comandos, módulos, plantillas o acceso a recursos.

**Consecuencia:** no existen callbacks, expresiones, `eval`, imports dinámicos, plugins, scripts ni parámetros libres. `splitComma` se limita a listas de cadenas y `parseJson` solo declara el análisis JSON de listas.

## D-04 — Ausencia, vacío y defecto son estados distintos

**Decisión:** una clave ausente no equivale a `CLAVE=`. Los valores por defecto se aplican únicamente a claves ausentes y cuentan como presentes para dependencias; un valor vacío permanece presente y se valida.

**Motivo:** sustituir silenciosamente valores vacíos con defectos ocultaría errores frecuentes de despliegue y haría las dependencias ambiguas.

**Consecuencia:** la secuencia de resolución, transformación, conversión y restricciones queda cerrada en [CONTRATO_V1.md](CONTRATO_V1.md). Las pruebas futuras deben cubrir los tres estados para cada tipo relevante.

## D-05 — Salidas JSON y códigos de proceso diferenciados

**Decisión:** éxito y errores utilizan envolturas JSON estables. El éxito se escribe solo en stdout; los errores solo en stderr. Los códigos son `0` para éxito/ayuda, `2` para uso, `3` para entrada, `4` para esquema, `5` para configuración y `1` para fallo interno seguro.

**Motivo:** el resultado debe ser consumible por automatización y distinguir una configuración incorrecta de un fallo en la definición o acceso de archivos.

**Consecuencia:** no se ofrece modo de texto alternativo en v1. Los mensajes son genéricos y los identificadores permiten que scripts y pruebas clasifiquen fallos sin analizar contenido sensible.

## D-06 — Modelo de secretos por redacción estricta

**Decisión:** `secret: true` impide exponer valores y derivados en cualquier salida pública. La herramienta tampoco muestra valores de variables no secretas, con lo que el resumen se limita a estado, origen, claves y advertencias.

**Motivo:** los diagnósticos y logs de CI suelen persistir; evitar valores por diseño reduce la superficie de filtración y simplifica la revisión de seguridad.

**Consecuencia:** los mensajes de error no incluyen valores, longitudes, hashes, prefijos, sufijos o representaciones transformadas. Las claves desconocidas se tratan como sensibles por defecto. Un valor real en `default` sigue estando prohibido en documentación y repositorio aunque la CLI futura lo redacte.

## D-07 — Tipos y listas deliberadamente limitados

**Decisión:** V1 ofrece `string`, `number`, `boolean`, `enum`, `url` y `list` de escalares homogéneos. Las listas se aportan como JSON o mediante `splitComma` para cadenas.

**Motivo:** cubre parámetros de aplicación habituales sin introducir parseo de estructuras anidadas, coerciones ambiguas o una sintaxis de lista configurable.

**Consecuencia:** no hay objetos, arrays anidados, valores `null`, unicidad, restricciones de elemento o CSV. Los booleanos solo aceptan `true`/`false` minúsculos tras transformaciones explícitas; no se aceptan equivalentes localizados.

## D-08 — Patrones limitados pero no ejecutables

**Decisión:** los patrones se declaran como `source` y flags `i`, `m`, `u`, se compilan durante la validación del esquema y se limitan a 256 unidades de código.

**Motivo:** separar patrón y flags impide modos dinámicos no documentados y permite detectar errores antes de revisar datos de configuración.

**Consecuencia:** no se soportan flags globales o dependientes de estado. Un patrón no ejecuta código, pero aún puede ser costoso; V1 documenta este riesgo y no se presenta como protección suficiente para entradas hostiles ilimitadas.

## D-09 — Dependencias declarativas sobre presencia válida

**Decisión:** `allOrNone`, `requires` y `forbids` se evalúan una vez terminadas la conversión y restricciones. Una clave cuenta como presente si procede del `.env` o de un defecto y ya es válida.

**Motivo:** evita que datos inválidos activen reglas secundarias confusas y deja una semántica estable para claves por defecto.

**Consecuencia:** las dependencias no crean ni transforman valores. Referencias desconocidas, claves repetidas dentro de grupos y reglas estructuralmente duplicadas invalidan el esquema antes de validar configuración.

## D-10 — Parser `.env` con semántica contractual

**Decisión:** la Fase 2 elegirá una dependencia mantenida para `.env`, pero solo podrá usarse si reproduce las reglas de asignación, vacío, duplicación, comentarios y ausencia de interpolación fijadas por [CONTRATO_V1.md](CONTRATO_V1.md).

**Motivo:** usar una biblioteca reduce errores de análisis, pero no debe expandir el contrato con comportamiento dependiente de shell o una versión concreta.

**Consecuencia:** si la biblioteca elegida acepta `export`, interpolación o sustituciones fuera de contrato, el adaptador futuro deberá rechazarlas o neutralizarlas. La selección y justificación de la dependencia se documentará en Fase 2.

## D-11 — Sin `.env.example` propio

**Decisión:** este proyecto no crea un archivo [`.env.example`](../.env.example) propio en V1.

**Motivo:** el validador recibe archivos objetivo explícitos; no tiene variables de ejecución ni requiere credenciales. Un archivo de ejemplo podría confundirse con configuración obligatoria de la propia herramienta.

**Consecuencia:** los ejemplos sintéticos futuros vivirán en [data/fixtures](../data/fixtures) y no contendrán secretos. Si una ampliación añade configuración de la herramienta, deberá crear un archivo de ejemplo sin valores reales.

## D-12 — Entorno reproducible con versiones exactas

**Decisión:** la Fase 2 usa Node.js `>=22.0.0` y npm `>=10.0.0`; fija `zod` `3.24.2`, `dotenv` `16.4.7`, TypeScript `5.8.2`, `@types/node` `22.14.1` y Prettier `3.5.3` como versiones exactas en [package.json](../package.json), con resolución reproducible en [package-lock.json](../package-lock.json). Las pruebas futuras usarán el runner nativo `node --test`.

**Motivo:** las versiones exactas y el lockfile hacen que instalación, compilación y formato sean repetibles. Zod satisface el modelado estricto de la Fase 3; dotenv aporta un parser mantenido, que la Fase 5 encapsulará para conservar la semántica limitada del contrato. El runner nativo evita añadir una dependencia de pruebas antes de que existan pruebas de comportamiento.

**Consecuencia:** los comandos de Fase 2 son `npm run build`, `npm run typecheck`, `npm run format:check`, `npm test` y `npm run quality`. La entrada `bin` se reserva para la Fase 5, sin exponer todavía una CLI funcional. El directorio raíz ya ignora `node_modules/`, `dist/` y artefactos de TypeScript, de modo que no se añade un `.gitignore` local redundante.

## Revisión de decisiones

La Fase 1 cierra el contrato y los escenarios en [CONTRATO_V1.md](CONTRATO_V1.md) y [ESCENARIOS_FASE_1.md](ESCENARIOS_FASE_1.md). La Fase 2 fija el entorno y la selección de dependencias; las Fases 3 y 4 implementarán el modelo de esquema y el motor puro; la Fase 5 adaptará archivos y CLI; la Fase 6 automatizará validaciones; y la Fase 7 documentará la entrega. Cualquier modificación posterior deberá indicar los escenarios, pruebas y criterios de aceptación afectados.
