# Decisiones de alcance — Divisor de gastos

Este documento registra las decisiones necesarias para concretar el proyecto 15. El índice raíz solo asigna «Divisor de gastos», categoría Utilidad y TypeScript; las decisiones siguientes definen la primera versión local. Cualquier cambio posterior deberá actualizar [README.md](../README.md), [ROADMAP.md](../ROADMAP.md), [CONTRATO_V1.md](CONTRATO_V1.md) y los escenarios afectados.

## D-01 — Una CLI local y un archivo JSON explícito

**Decisión:** la v1 será una CLI `expense-splitter` que recibe exactamente una ruta a un archivo JSON. La ayuda se admite únicamente aislada con `--help` o `-h`.

**Motivo:** un único archivo autocontenido hace visible el conjunto completo de participantes y gastos, evita estado implícito y permite resultados reproducibles.

**Consecuencia:** no hay modo interactivo, entrada estándar, interfaz web, carga automática, múltiples archivos ni opciones de ejecución adicionales. Las rutas relativas son responsabilidad normal del directorio de trabajo de quien invoca la CLI.

## D-02 — Reparto igualitario por gasto entre una lista explícita

**Decisión:** cada gasto declara un pagador y la lista exacta de participantes que asumen su coste. El importe se divide en partes iguales solo entre `splitAmong`; el pagador puede o no pertenecer a esa lista.

**Motivo:** representa un flujo básico de gastos compartidos sin introducir ponderaciones, porcentajes ni reglas implícitas.

**Consecuencia:** no hay reparto global por grupo, participantes implícitos ni reglas particulares adicionales por gasto. Repartos ponderados, importes manuales y porcentajes quedan para una versión posterior.

## D-03 — Unidades menores enteras y reparto de restos por orden declarado

**Decisión:** todos los importes usan `amountMinor`, un entero seguro de unidades menores. Al dividir un importe indivisible, las primeras personas de `splitAmong` reciben una unidad adicional hasta agotar el resto.

**Motivo:** evita errores de coma flotante y hace que la suma de cuotas sea siempre igual al gasto original.

**Consecuencia:** la moneda se declara mediante un único código ISO 4217 de tres letras, pero la herramienta no conoce ni aplica su número de decimales; el significado de la unidad menor queda en quien prepara el archivo. El orden de `splitAmong` es significativo para el redondeo.

## D-04 — Balances netos y transferencias deterministas, no óptimas

**Decisión:** la salida presenta balances por participante y propone transferencias entre deudores y acreedores ordenados por `participantId`.

**Motivo:** los balances explican el reparto y las transferencias ofrecen un resultado accionable sin depender de pagos externos.

**Consecuencia:** el algoritmo no intenta minimizar globalmente el número de operaciones ni conservar relaciones de pago originales. Las transferencias son sugerencias de liquidación, no instrucciones de pago reales.

## D-05 — Identificadores técnicos y nombres visibles separados

**Decisión:** participantes y gastos tienen identificadores técnicos únicos; los participantes también tienen un nombre visible que no necesita ser único.

**Motivo:** las referencias estables no deben depender de etiquetas de presentación repetibles o modificables.

**Consecuencia:** `paidBy` y `splitAmong` referencian `id`, nunca `name`. Los nombres y descripciones se preservan como datos de presentación y no se usarán para deduplicar.

## D-06 — Validación estricta y sin corrección automática

**Decisión:** el documento JSON admite solo campos documentados y rechaza campos desconocidos, identificadores repetidos, referencias ausentes, textos vacíos e importes inválidos.

**Motivo:** una entrada estricta permite que el futuro núcleo sea determinista y evita que decisiones silenciosas alteren un reparto económico.

**Consecuencia:** la herramienta no rellena participantes, no elimina duplicados, no normaliza identificadores ni convierte importes decimales. Los errores públicos no incluyen valores de entrada.

## D-07 — Sin persistencia, secretos ni integraciones externas

**Decisión:** la v1 opera sobre un único archivo durante una ejecución y no requiere variables de entorno, credenciales ni servicios externos.

**Motivo:** mantiene el microproyecto local, atómico y demostrable según el flujo diario del repositorio.

**Consecuencia:** no se crea [`.env.example`](../.env.example) local. Los fixtures futuros deberán ser sintéticos y las extensiones que introduzcan una integración deberán tener un fallback local documentado.

## D-08 — Entorno Node.js 22, npm y herramientas de calidad locales

**Decisión:** la Fase 2 usa Node.js `>=22.0.0`, npm `>=10.0.0`, TypeScript `5.8.2`, Prettier `3.5.3` y `@types/node` `22.14.1`. Se fija el gestor mediante el archivo [`package-lock.json`](../package-lock.json) y no se añaden dependencias de producción.

**Motivo:** Node.js aporta la futura base de la CLI local y TypeScript garantiza el tipado estricto del núcleo. Prettier cubre el formato sin introducir un linter adicional antes de que exista código de dominio. Las versiones fijadas mantienen una instalación reproducible y siguen las convenciones recientes de proyectos TypeScript vecinos.

**Consecuencia:** [`package.json`](../package.json) expone comandos aislados para compilación, verificación de tipos, formato, pruebas y la comprobación agregada `quality`. La compilación solo considera [`src`](../src); durante esta fase contiene una declaración de módulo mínima y no implementa el dominio, la CLI ni validaciones. Los artefactos locales `node_modules`, `dist`, cobertura y archivos de compilación incremental se excluyen en [`.gitignore`](../.gitignore).

## D-09 — Núcleo puro que recibe valores ya cargados

**Decisión:** el núcleo público `splitExpenses(input)` recibe un valor JavaScript desconocido, lo valida frente al contrato v1 y devuelve el resultado tipado o lanza `DomainValidationError` con incidencias de dominio ordenadas. No lee rutas, JSON, argumentos, entrada estándar ni variables de entorno.

**Motivo:** centraliza la validación y el cálculo determinista sin acoplarlos al futuro adaptador de CLI. Así, la Fase 4 solo tendrá que convertir archivo y argumentos en valores para el núcleo y serializar su resultado o error.

**Consecuencia:** [`src/types.ts`](../src/types.ts) representa el documento, las salidas y las incidencias; [`src/validation.ts`](../src/validation.ts) aplica las reglas estructurales y de referencias; y [`src/expense-splitter.ts`](../src/expense-splitter.ts) acumula importes seguros, asigna restos por orden y genera transferencias. Los fallos de lectura, UTF-8, JSON, canales y códigos de proceso siguen fuera del núcleo y pertenecen a la Fase 4.

## D-10 — Adaptador CLI mínimo con errores públicos seguros

**Decisión:** la Fase 4 implementa [`src/cli.ts`](../src/cli.ts) como adaptador de la CLI. Acepta una única ruta o ayuda aislada, lee solo un archivo regular UTF-8, elimina un BOM inicial, interpreta JSON y delega el valor en `splitExpenses`. La salida correcta se emite por salida estándar; los fallos se emiten por salida de error como un único JSON con categoría, código, mensaje estable e incidencias cuando proceda.

**Motivo:** preserva el núcleo puro y hace operable el contrato local sin añadir dependencias ni efectos secundarios al cálculo.

**Consecuencia:** la CLI asigna los códigos de proceso documentados: `0` para éxito o ayuda, `2` para uso, `3` para entrada, `4` para validación y `1` para fallos internos controlados. Los diagnósticos no incluyen rutas absolutas, contenido de entrada ni trazas. El fixture [`data/fixtures/viaje.json`](../data/fixtures/viaje.json) es exclusivamente sintético.

## D-11 — Regresión pública compilada con fixture esperado

**Decisión:** [`tests/domain.test.mjs`](../tests/domain.test.mjs) importa el núcleo compilado para comprobar reglas puras; [`tests/cli.test.mjs`](../tests/cli.test.mjs) lanza [`dist/cli.js`](../dist/cli.js) como proceso independiente. `npm test` compila antes de ejecutar ambos grupos. El fixture principal se compara con [`data/expected/viaje-result.json`](../data/expected/viaje-result.json) y las entradas límite se crean en directorios temporales que cada prueba elimina.

**Motivo:** verifica tanto el comportamiento de dominio como la interfaz distribuible, incluyendo canales y códigos de proceso, sin acoplar las pruebas a internals no públicos ni a estado persistente.

**Consecuencia:** los resultados esperados quedan versionados, el determinismo se comprueba mediante ejecuciones repetidas y la suite no usa red, secretos, datos reales ni archivos temporales persistentes. La salida `dist` es un artefacto de compilación local y no forma parte de los archivos controlados.

## Revisión de decisiones

La Fase 1 cierra el contrato y sus escenarios en [CONTRATO_V1.md](CONTRATO_V1.md) y [ESCENARIOS_FASE_1.md](ESCENARIOS_FASE_1.md). La Fase 2 selecciona y verifica el entorno TypeScript. La Fase 3 implementa el modelo, validación y cálculo puro. La Fase 4 añade el adaptador de CLI y el flujo local mínimo. La Fase 5 automatiza pruebas de dominio, interfaz y regresión. La Fase 6 documentará la entrega. Cualquier modificación posterior deberá indicar los escenarios, pruebas y criterios de aceptación afectados.
