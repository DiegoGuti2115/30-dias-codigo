# Roadmap — Divisor de gastos

Este roadmap organiza el desarrollo del proyecto 15 como una utilidad TypeScript para dividir gastos. Las Fases 0 a 6 han cerrado el contrato, el entorno, el núcleo, la CLI local reproducible, las pruebas de regresión completas y la entrega .

## Objetivo de la primera versión funcional

Entregar una utilidad local que permita dividir gastos conforme a una regla documentada, valide las entradas necesarias y presente un resultado reproducible. La interfaz, el formato de datos, la regla de reparto, la precisión monetaria y el formato de salida se decidirán en la Fase 1; no están definidos en esta entrega.

## Prioridades

- **P0:** cerrar el alcance, el contrato de datos, la regla de reparto, la precisión monetaria, el comportamiento ante errores y una ruta local verificable.
- **P1:** implementar el flujo principal, validarlo con pruebas y documentar una demostración reproducible.
- **P2:** evaluar mejoras solo después de que exista una versión funcional y probada, sin ampliar el alcance comprometido de P0.

## Secuencia y dependencias

```text
Fase 0 → Fase 1 → Fase 2 → Fase 3 → Fase 4 → Fase 5 → Fase 6
                    │         │         │
                    └─────────┴─────────┴── pruebas y fixtures progresivos
```

- La Fase 1 resuelve todas las decisiones pendientes antes de la implementación y es la fuente de verdad funcional junto con [docs/CONTRATO_V1.md](docs/CONTRATO_V1.md).
- La Fase 2 depende del contrato de la Fase 1, pues las dependencias y la estructura ejecutable deben responder a una interfaz acordada.
- La Fase 3 utiliza el contrato y el entorno para crear el núcleo de cálculo sin acoplarlo innecesariamente a una interfaz.
- La Fase 4 integra el núcleo en la interfaz elegida y añade validación de entradas y presentación de resultados.
- La Fase 5 verifica las reglas, errores y resultados definidos en las fases previas.
- La Fase 6 solo se inicia tras validar el flujo principal y prepara documentación, demo y revisión final.

## Fase 0 — Preparación documental y estructural — Completada

**Objetivo:** reservar una ubicación coherente para el proyecto y describir sin inventar el alcance aún no especificado.

**Entregables:**

- Directorio [projects/day-15-expense-splitter](.) alineado con el enlace del [índice raíz](../../README.md).
- [README.md](README.md) con propósito, límites, decisiones pendientes, estructura y uso conceptual.
- Este roadmap con fases, dependencias y condiciones de salida.
- Directorios [docs](docs), [src](src), [tests](tests), [data/fixtures](data/fixtures), [data/expected](data/expected) y [assets](assets).

**Dependencias:** ninguna.

**Criterios de finalización:**

- La documentación distingue de forma explícita la información confirmada de las decisiones pendientes.
- No existen funcionalidades, código ejecutable, dependencias, pruebas funcionales ni fixtures que simulen una especificación no aprobada.
- La estructura sigue la convención general de proyectos establecida en el [README raíz](../../README.md).

## Fase 1 — Definición funcional y contrato — Completada, P0

**Objetivo:** convertir «Divisor de gastos» en un comportamiento inequívoco y comprobable.

**Entregables completados:**

- [docs/CONTRATO_V1.md](docs/CONTRATO_V1.md) como fuente de verdad para la CLI, el JSON de entrada, la validación, el reparto igualitario, unidades menores, restos, balances, transferencias, salidas, errores y límites de v1.
- [docs/DECISIONES.md](docs/DECISIONES.md) con las decisiones locales sobre interfaz, modelo de gasto, precisión, orden determinista, referencias y exclusiones.
- [docs/ESCENARIOS_FASE_1.md](docs/ESCENARIOS_FASE_1.md) con vectores documentales de reparto exacto, reparto con resto, balances, transferencias, documento mínimo, validaciones e interfaz futura.
- [README.md](README.md) actualizado con el alcance cerrado, la interfaz prevista y las reglas relevantes, sin presentarlas como funcionalidad ya ejecutable.

**Decisiones cerradas:**

- La interfaz v1 será una CLI local `expense-splitter` que recibe una única ruta JSON explícita, o ayuda aislada mediante `--help` o `-h`.
- El documento declara `version: "v1"`, una única moneda ISO 4217, de 2 a 50 participantes y de 1 a 500 gastos.
- Cada gasto declara identificador, descripción, entero positivo `amountMinor`, pagador `paidBy` y una lista explícita, no vacía y sin repetidos `splitAmong`.
- El reparto inicial es igualitario por gasto. Los restos se asignan en unidades menores a las primeras personas de `splitAmong`, según el orden declarado.
- La salida incluirá balances ordenados por `participantId` y transferencias deterministas entre deudores y acreedores ordenados por ese mismo identificador; no se promete optimización global.
- Persistencia, red, secretos, autenticación, pagos, interfaz gráfica, múltiples monedas, conversión y reglas de reparto avanzadas quedan fuera de v1.

**Dependencias:** Fase 0.

**Criterios de finalización:**

- Completado: un flujo válido e inválido se describe sin ambigüedad mediante el contrato y el catálogo de escenarios.
- Completado: las fases posteriores pueden implementar los cálculos sin decidir reglas implícitas.
- Completado: precisión, unidades menores, redondeo, reparto de restos, balances y resultados esperados están documentados.
- Completado: el alcance P0 queda limitado y las extensiones se difieren a P2.

**Límite de fase:** no se ha creado implementación TypeScript, manifiesto npm, configuración de compilación, dependencia, fixture ejecutable, prueba automatizada ni demo. Esos elementos continúan en las Fases 2 a 6.

## Fase 2 — Entorno TypeScript y calidad — Completada, P0

**Objetivo:** preparar un entorno reproducible y mínimo, coherente con la interfaz aprobada.

**Entregables completados:**

- [`package.json`](package.json) y [`package-lock.json`](package-lock.json) aislados en el proyecto, con Node.js `>=22`, npm `>=10`, TypeScript, Prettier y tipos de Node.js como únicas dependencias de desarrollo.
- [`tsconfig.json`](tsconfig.json) con compilación NodeNext y opciones de tipado estricto; [`src/environment.d.ts`](src/environment.d.ts) permite comprobar la estructura inicial sin implementar dominio.
- Scripts `build`, `typecheck`, `test`, `format`, `format:check` y `quality` en el manifiesto.
- [`.prettierrc.json`](.prettierrc.json) y [`.gitignore`](.gitignore) locales que fijan formato y excluyen `node_modules`, `dist`, cobertura y metadatos de compilación.
- Instalación local reproducible mediante `npm ci`, documentada en [`README.md`](README.md), sin secretos ni servicios externos.

**Dependencias:** Fase 1.

**Criterios de finalización:**

- Completado: la instalación está documentada y no requiere secretos ni servicios externos.
- Completado: los comandos de calidad funcionan sobre la estructura inicial.
- Completado: las dependencias están aisladas en el proyecto y justificadas por la futura CLI TypeScript y los controles de calidad.

**Límite de fase:** no se ha implementado el modelo, las validaciones, el cálculo, la CLI, fixtures funcionales ni pruebas de escenarios; corresponden a las Fases 3 a 5.

## Fase 3 — Núcleo de reparto y modelo de dominio — Completada, P0

**Objetivo:** implementar un núcleo TypeScript determinista que aplique el contrato de reparto sin depender de la interfaz.

**Entregables completados:**

- [`src/types.ts`](src/types.ts) modela el documento v1, participantes, gastos, balances, transferencias e incidencias de dominio.
- [`src/validation.ts`](src/validation.ts) valida campos cerrados, cardinalidades, texto, importes seguros, identificadores, referencias y repartos; los fallos de dominio se exponen como `DomainValidationError` con incidencias ordenadas.
- [`src/expense-splitter.ts`](src/expense-splitter.ts) exporta el núcleo puro `splitExpenses(input)`, que acumula unidades menores, distribuye restos según el orden declarado y propone transferencias deterministas por identificador.
- El núcleo no lee archivos ni argumentos, no serializa JSON, no usa red, persistencia, credenciales ni configuración de proceso.

**Dependencias:** Fases 1 y 2.

**Criterios de finalización:**

- Completado: las mismas entradas válidas producen los mismos resultados mediante aritmética de enteros seguros y orden explícito.
- Completado: `DomainValidationError` separa las incidencias de contrato de los futuros fallos de lectura o CLI.
- Completado: el núcleo implementa reparto, restos, acumulación, balances y liquidación de los escenarios documentados; su regresión automatizada completa continúa en la Fase 5.

**Límite de fase:** no se ha creado adaptador de CLI, lectura de archivos, interpretación JSON, canales de salida, códigos de proceso, fixtures ejecutables ni suite de regresión; corresponden a las Fases 4 y 5.

## Fase 4 — Interfaz local y flujo principal — Completada, P0

**Objetivo:** exponer el núcleo a través de la interfaz seleccionada y completar el recorrido de usuario acordado.

**Entregables completados:**

- [`src/cli.ts`](src/cli.ts) expone `expense-splitter` mediante una única ruta explícita o ayuda aislada, respetando los canales y códigos de proceso del contrato.
- El adaptador lee únicamente archivos regulares UTF-8, admite BOM inicial, interpreta JSON estricto y entrega el valor al núcleo `splitExpenses` sin duplicar reglas de dominio.
- La salida correcta usa un único JSON por salida estándar; errores de uso, entrada, validación e internos usan un único JSON seguro por salida de error.
- [`data/fixtures/viaje.json`](data/fixtures/viaje.json) proporciona un flujo sintético local sin información personal ni secretos.
- [`README.md`](README.md) documenta instalación, compilación e invocación verificable de la CLI.

**Dependencias:** Fase 3.

**Criterios de finalización:**

- Completado: una persona puede compilar y ejecutar el flujo principal siguiendo las instrucciones locales.
- Completado: las entradas inválidas reciben una respuesta JSON controlada, sin rutas absolutas, contenido ni trazas.
- Completado: el fixture de demostración contiene exclusivamente datos sintéticos y no requiere secretos.

**Límite de fase:** no se ha añadido una suite de regresión automatizada ni resultados esperados; corresponden a la Fase 5.

## Fase 5 — Pruebas y regresión — Completada, P1

**Objetivo:** demostrar que la utilidad mantiene el comportamiento contratado en cálculos y errores.

**Entregables completados:**

- [`tests/domain.test.mjs`](tests/domain.test.mjs) cubre reparto exacto, restos por orden declarado, acumulación, liquidación, conservación, determinismo y categorías de validación documentadas.
- [`tests/cli.test.mjs`](tests/cli.test.mjs) ejecuta la interfaz pública compilada y verifica ayuda, uso, archivo, UTF-8, JSON, BOM, validación, canales y códigos de proceso.
- [`data/expected/viaje-result.json`](data/expected/viaje-result.json) fija el resultado sintético del fixture principal para regresión determinista.
- `npm test` compila el proyecto y ejecuta los tests `*.test.mjs` sin red, credenciales ni datos reales.

**Dependencias:** Fases 3 y 4.

**Criterios de finalización:**

- Completado: los escenarios relevantes de cálculo, validación e interfaz de la Fase 1 tienen cobertura automatizada reproducible.
- Completado: el flujo principal y los límites acordados pasan de forma consistente con resultados y errores públicos comprobados.
- Completado: la suite usa únicamente fixtures sintéticos locales y directorios temporales limpiados por cada prueba.

## Fase 6 — Documentación, demo y entrega — P1

**Objetivo:** dejar una versión funcional entendible, demostrable y coherente con el proceso del reto.

**Tareas:**

- Actualizar [README.md](README.md) con requisitos reales, instalación, configuración, uso, límites y estructura final.
- Añadir documentación adicional en [docs](docs) solo cuando sea necesaria para el contrato o la operación local.
- Crear un guion y recurso de demostración de hasta 15 segundos en [assets](assets), usando datos sintéticos.
- Revisar enlaces, comandos, dependencias, estructura y ausencia de secretos.
- Confirmar los elementos de entrega aplicables de [docs/DAILY_WORKFLOW.md](../../docs/DAILY_WORKFLOW.md).

**Dependencias:** Fases 1 a 5.

**Criterios de finalización:**

- La documentación describe exclusivamente comportamiento existente y comprobado.
- La demo muestra entrada, acción y resultado sin datos sensibles.
- Instalación, uso y pruebas se pueden reproducir localmente.

## Mejoras posteriores — P2

Estas posibilidades no forman parte del alcance actual y solo se evaluarán tras cerrar la primera versión:

- Reglas de reparto adicionales.
- Persistencia local o importación/exportación de datos.
- Optimización de transferencias para liquidar saldos, si no fuera parte del contrato de v1.
- Interfaz alternativa o mejoras visuales.
- Internacionalización, soporte de múltiples monedas o gestión avanzada de redondeos.
- Integraciones externas, únicamente si aportan valor directo y disponen de fallback local conforme al proceso del repositorio.

Cada mejora requerirá especificación, pruebas y actualización documental antes de implementarse.

## Riesgos generales y mitigación

| Riesgo                                     | Mitigación                                                                                  |
| ------------------------------------------ | ------------------------------------------------------------------------------------------- |
| Reglas de reparto ambiguas                 | Cerrar contrato y ejemplos antes de escribir el núcleo de cálculo.                          |
| Errores de precisión o redondeo            | Definir representación monetaria y escenarios de resto en la Fase 1; cubrirlos con pruebas. |
| Ampliación prematura del alcance           | Mantener P0 en un único flujo local y relegar extensiones a P2.                             |
| Dependencias innecesarias                  | Seleccionarlas solo después de definir interfaz y necesidades verificables.                 |
| Datos sensibles en la demo                 | Usar exclusivamente nombres e importes sintéticos.                                          |
| Integración externa que bloquee la entrega | Evitarla en P0; si se incorpora después, exigir un fallback local.                          |

## Criterio de salida de la primera versión

La primera versión estará lista cuando las Fases 1 a 6 estén aceptadas: existirá una utilidad local TypeScript con un contrato de reparto cerrado, cálculo determinista, validación de entradas, resultados documentados, pruebas o verificaciones reproducibles, datos sintéticos y una demostración breve coherente con la documentación.
