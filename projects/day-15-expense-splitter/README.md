# Día 15 — Divisor de gastos

> Proyecto de utilidad del reto [30 Días, 30 Proyectos](../../README.md). **Estado:** Fases 0 a 4 completadas; la CLI local y el núcleo de dominio están disponibles.

## Propósito

Divisor de gastos es una utilidad TypeScript local que, en su futura versión 1, calculará cómo se distribuye un conjunto de gastos entre participantes. A partir de un único documento JSON explícito, producirá balances netos y transferencias sugeridas para saldarlos de forma determinista.

El contrato funcional de la versión 1 está definido en [docs/CONTRATO_V1.md](docs/CONTRATO_V1.md). Este README ofrece una visión de alcance; el contrato prevalece ante cualquier diferencia de detalle.

## Alcance cerrado de la versión 1

- Exponer una CLI local llamada `expense-splitter`.
- Recibir una única ruta explícita a un archivo JSON UTF-8.
- Definir participantes mediante identificadores técnicos únicos y nombres visibles.
- Registrar gastos con identificador, descripción, importe entero en unidades menores, pagador y participantes que asumen el coste.
- Repartir cada gasto de manera igualitaria entre los integrantes explícitos de `splitAmong`.
- Distribuir los restos de una división no exacta según el orden declarado de `splitAmong`.
- Calcular importes pagados, importes adeudados y balance neto para cada participante.
- Producir transferencias de liquidación deterministas entre deudores y acreedores.
- Validar datos estructurales, importes, referencias y duplicados antes del cálculo.
- Separar salida correcta, errores y códigos de proceso conforme al contrato.

## Fuera de alcance

- Persistencia, edición, historial, grupos guardados o carga automática de archivos.
- Entrada estándar, modo interactivo, API HTTP, interfaz gráfica, autenticación o cuentas.
- Pagos reales, enlaces de cobro, servicios de terceros, red, telemetría, secretos o variables de entorno.
- Conversión de divisas, múltiples monedas por documento, impuestos, propinas, descuentos o presupuestos.
- Repartos ponderados, porcentajes, acciones, cuotas manuales o reglas de reparto distintas del reparto igualitario v1.
- Optimización global del número mínimo de transferencias.

## Interfaz local

La CLI `expense-splitter` está implementada y admite exclusivamente:

```text
expense-splitter <ruta-entrada.json>
expense-splitter --help
expense-splitter -h
```

| Situación                          | Canal                              | Código |
| ---------------------------------- | ---------------------------------- | :----: |
| Cálculo válido                     | Resultado JSON por salida estándar |  `0`   |
| Ayuda aislada                      | Texto plano por salida estándar    |  `0`   |
| Uso inválido                       | Error JSON por salida de error     |  `2`   |
| Archivo o JSON de entrada inválido | Error JSON por salida de error     |  `3`   |
| Datos que incumplen el contrato    | Error JSON por salida de error     |  `4`   |
| Fallo interno controlable          | Error JSON por salida de error     |  `1`   |

La herramienta interpreta la ruta exactamente como se recibe, por lo que una ruta relativa se resuelve desde el directorio de trabajo. No busca archivos ni acepta entrada estándar, opciones adicionales o más de una ruta.

## Modelo de datos y flujo esperado

El archivo de entrada será un objeto JSON `v1` con una moneda, de dos a cincuenta participantes y de uno a quinientos gastos. Un gasto declara quién pagó y quiénes participan expresamente en el reparto.

```text
Preparar participantes y gastos en un JSON explícito
→ Validar estructura, identificadores, importes y referencias
→ Dividir cada gasto entre sus participantes declarados
→ Acumular pagado, adeudado y balance por persona
→ Generar transferencias deterministas para saldar balances
→ Emitir el resultado JSON o un error estructurado
```

La gramática completa, los campos obligatorios y los formatos de resultado están en [docs/CONTRATO_V1.md](docs/CONTRATO_V1.md).

## Regla de reparto y precisión monetaria

Todos los importes usan enteros seguros en unidades menores y se almacenan como `amountMinor`. La herramienta no aceptará decimales ni realizará conversión de divisas. Para un gasto de importe `A` entre `N` personas se asigna `floor(A / N)` a cada una, y las primeras `A % N` personas de `splitAmong` reciben una unidad menor adicional.

Este criterio garantiza que todas las cuotas suman exactamente el importe original y evita errores de coma flotante. El pagador no se añade automáticamente a `splitAmong`: un gasto puede ser pagado por una persona y repartido entre otras.

Los balances se calculan como `pagado - adeudado`. Los acreedores y deudores se ordenarán por identificador para generar transferencias reproducibles; dicha secuencia no pretende ser una optimización global del número de pagos.

## Validaciones y errores previstos

La futura implementación rechazará, entre otros casos:

- Raíz JSON, campos o versión no compatibles con `v1`.
- Moneda no declarada como código ASCII de tres letras mayúsculas.
- Menos de dos participantes, falta de gastos o cardinalidades fuera de los límites definidos.
- Identificadores inválidos o repetidos.
- Nombres y descripciones vacíos tras recorte Unicode.
- Importes que no sean enteros seguros estrictamente positivos en unidades menores.
- Pagadores o personas de reparto inexistentes.
- Listas `splitAmong` vacías o con referencias repetidas.

Los identificadores de error, categorías, mensajes principales, rutas y orden de incidencias están definidos en el [contrato](docs/CONTRATO_V1.md). Los escenarios trazables para cálculos, restos, balances, transferencias y errores están en [docs/ESCENARIOS_FASE_1.md](docs/ESCENARIOS_FASE_1.md).

## Requisitos, instalación y configuración

El entorno local no requiere servicios externos ni credenciales:

- Node.js `>=22.0.0` y npm `>=10.0.0`.
- TypeScript `5.8.2`, Prettier `3.5.3` y tipos de Node.js como dependencias de desarrollo fijadas en [`package-lock.json`](package-lock.json).
- No hay archivo `.env.example` local ni variables de entorno.

Desde este directorio, instalar y verificar el entorno:

```text
npm ci
npm run quality
```

Compilar y ejecutar el flujo principal con el fixture sintético incluido:

```text
npm run build
node dist/cli.js ./data/fixtures/viaje.json
```

También se puede invocar el binario local tras compilar:

```text
npm exec expense-splitter -- ./data/fixtures/viaje.json
```

La salida correcta es un único JSON por salida estándar. Los errores se escriben como un único JSON por salida de error y usan los códigos de proceso del contrato: uso `2`, entrada `3`, validación `4` e interno controlado `1`.

| Comando                | Función actual                                                      |
| ---------------------- | ------------------------------------------------------------------- |
| `npm run build`        | Compila la fuente TypeScript de [`src`](src) en `dist`.             |
| `npm run typecheck`    | Comprueba el tipado estricto sin generar salida.                    |
| `npm test`             | Compila y ejecuta pruebas de dominio, CLI y regresión por fixtures. |
| `npm run format`       | Aplica Prettier a los archivos controlados del proyecto.            |
| `npm run format:check` | Comprueba el formato sin modificar archivos.                        |
| `npm run quality`      | Ejecuta typecheck, comprobación de formato y pruebas.               |

## Decisiones técnicas

- **CLI y JSON explícito:** permiten una entrada autocontenida, portable y reproducible.
- **Separación de dominio e interfaz:** el núcleo de cálculo permanece puro; la CLI adapta rutas, archivos, canales y códigos de proceso sin duplicar reglas.
- **Unidades menores enteras:** evitan la aritmética monetaria de coma flotante y hacen verificable el tratamiento de restos.
- **Referencias por identificador:** los nombres visibles no se usan como claves y pueden repetirse sin ambigüedad.
- **Liquidación determinista no óptima:** la previsibilidad y la trazabilidad prevalecen sobre algoritmos de optimización fuera de alcance.
- **Sin integración externa:** no hay dependencia de red; cualquier ampliación futura deberá cumplir la política de fallback de [docs/DAILY_WORKFLOW.md](../../docs/DAILY_WORKFLOW.md).

El razonamiento y las consecuencias de cada decisión están registrados en [docs/DECISIONES.md](docs/DECISIONES.md).

## Estructura del proyecto

```text
projects/day-15-expense-splitter/
├── README.md
├── ROADMAP.md
├── docs/
│   ├── CONTRATO_V1.md
│   ├── DECISIONES.md
│   └── ESCENARIOS_FASE_1.md
├── package.json          # Manifiesto y comandos de calidad locales
├── package-lock.json     # Resolución reproducible de dependencias
├── tsconfig.json         # Compilación TypeScript estricta
├── .prettierrc.json      # Política de formato local
├── .gitignore            # Artefactos locales excluidos
├── src/
│   ├── types.ts          # Tipos de entrada, salida e incidencias de dominio
│   ├── validation.ts     # Validación estricta del contrato v1
│   ├── expense-splitter.ts # Cálculo puro de reparto y liquidación
│   └── cli.ts            # Adaptador de argumentos, archivo, JSON y canales de proceso
├── tests/                # Pruebas automatizadas de dominio, CLI y regresión
├── data/
│   ├── fixtures/         # Entradas sintéticas para la CLI
│   └── expected/         # Resultados sintéticos versionados
└── assets/               # Guion y recurso de demostración futuros
```

| Ruta                                                               | Responsabilidad                                                                       |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------- |
| [README.md](README.md)                                             | Alcance de v1, guía de orientación y estado de la fase.                               |
| [ROADMAP.md](ROADMAP.md)                                           | Fases, prioridades, dependencias y criterios de salida.                               |
| [docs/CONTRATO_V1.md](docs/CONTRATO_V1.md)                         | Fuente de verdad de interfaz, datos, cálculos, validaciones, resultados y límites v1. |
| [docs/DECISIONES.md](docs/DECISIONES.md)                           | Registro de decisiones locales tomadas ante vacíos del índice raíz.                   |
| [docs/ESCENARIOS_FASE_1.md](docs/ESCENARIOS_FASE_1.md)             | Vectores documentales para la implementación y las pruebas futuras.                   |
| [package.json](package.json)                                       | Manifiesto npm y comandos de compilación, tipo, formato y pruebas.                    |
| [tsconfig.json](tsconfig.json)                                     | Opciones TypeScript estrictas y salida local `dist`.                                  |
| [src/types.ts](src/types.ts)                                       | Tipos estrictos de documento, salida e incidencias.                                   |
| [src/validation.ts](src/validation.ts)                             | Validación pura y `DomainValidationError`.                                            |
| [src/expense-splitter.ts](src/expense-splitter.ts)                 | Función `splitExpenses(input)` para cálculo determinista sin E/S.                     |
| [src/cli.ts](src/cli.ts)                                           | Adaptador de CLI, lectura UTF-8, interpretación JSON y errores públicos.              |
| [tests](tests)                                                     | Pruebas de cálculo, validación, regresión por fixture y CLI pública.                  |
| [data/fixtures/viaje.json](data/fixtures/viaje.json)               | Documento sintético para ejecutar el flujo principal local.                           |
| [data/expected/viaje-result.json](data/expected/viaje-result.json) | Resultado esperado y versionado del fixture principal.                                |
| [assets](assets)                                                   | Recurso de demostración de hasta 15 segundos en la fase de entrega.                   |

## Estrategia de verificación

La Fase 5 automatiza cálculo, validación y CLI mediante el ejecutor nativo de Node.js. Las pruebas de dominio verifican reparto, redondeo, conservación y determinismo; las de CLI ejecutan el artefacto compilado y comprueban salida estándar, error estándar y códigos de proceso. El fixture sintético se contrasta con un resultado esperado versionado. La suite no depende de red, datos reales, secretos, configuración regional ni zona horaria.

## Arquitectura de interfaz

El adaptador [`src/cli.ts`](src/cli.ts) lee un único archivo regular como UTF-8, elimina un BOM inicial cuando existe, interpreta JSON estricto y entrega el valor a `splitExpenses`. Si el núcleo lanza `DomainValidationError`, la CLI conserva sus incidencias ordenadas y las serializa en el canal de error. La lectura de archivos, interpretación JSON, serialización y códigos de proceso permanecen fuera del núcleo puro.

## Estado de esta entrega

Las Fases 0 a 5 están completadas. El proyecto dispone del contrato v1, una CLI local reproducible, fixtures sintéticos con resultado esperado y una suite automatizada para núcleo e interfaz, sin red, persistencia ni credenciales. Sigue pendiente la documentación/demostración de entrega de la Fase 6.
