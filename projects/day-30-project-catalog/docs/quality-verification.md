# Verificación de calidad

## Objetivo

Estas comprobaciones mantienen una línea base reproducible para el Catálogo de proyectos. La suite usa únicamente el fixture local [`data/projects.json`](../data/projects.json), por lo que no requiere red, secretos ni cuentas externas; los destinos de **Código** se validan como URLs del monorepo público de GitHub sin solicitarlas.

## Comandos obligatorios

Ejecutar desde la raíz del proyecto, en este orden:

```bash
npm run lint
npm test
npm run build
git diff --check
git status --short
```

- `npm run lint` revisa el código TypeScript, React y la configuración de Next.js.
- `npm test` ejecuta pruebas de contrato, carga, filtros, presentación, accesibilidad, recuperación e interacción en JSDOM.
- `npm run build` valida tipos, renderizado estático y la compilación de producción de Next.js.
- `git diff --check` detecta espacios en blanco inválidos en los cambios rastreados.
- `git status --short` permite confirmar que no se incluyen artefactos generados, secretos ni cambios accidentales.

## Cobertura de regresión actual

| Área | Protección automatizada |
| --- | --- |
| Contrato | Versión, estructura estricta, IDs y días únicos, metadatos locales, URLs GitHub restringidas al proyecto correspondiente y campos inesperados. |
| Carga | Fixture local de 30 proyectos, orden de días, destinos GitHub coincidentes, datos inválidos y errores de lectura. |
| Dominio | Búsqueda por texto, filtros combinados, normalización de consulta, resultados vacíos y opciones únicas ordenadas. |
| Interfaz | Landmarks, enlace de salto, jerarquía de encabezados, colección completa, enlaces GitHub y estados del catálogo. |
| Interacción | Búsqueda, selectores nativos, contador anunciado, restablecimiento, recuperación de cero resultados y foco por teclado. |
| Errores | Recuperación de error de fuente y límite de error de App Router. |

La limpieza de DOM se centraliza en [`tests/setup.ts`](../tests/setup.ts) para que cada prueba de componente quede aislada y no acumule renders entre casos.

## Verificaciones manuales

Ejecutar también la matriz de [`accessibility-test-matrix.md`](accessibility-test-matrix.md) para teclado, lector de pantalla, viewport móvil, zoom, contraste, reducción de movimiento y recuperación.

## Limitaciones conocidas y priorizadas

- JSDOM no sustituye una revisión con lector de pantalla real ni una auditoría de contraste renderizada; ambas se mantienen en la matriz manual antes de publicar.
- La suite no realiza pruebas end-to-end en un navegador real porque el MVP local no necesita una dependencia adicional para su flujo actual. La navegación de filtros, recuperación y enlaces se cubre con Testing Library; el destino GitHub se valida en el esquema, sin requerir una solicitud de red.
- No existe fuente remota intencionalmente. Cualquier integración futura debe conservar el fixture local, añadir pruebas de fallo del proveedor y revisar estos comandos antes de incorporarse.
