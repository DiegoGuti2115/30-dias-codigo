# Día 21 — Dashboard de métricas

Aplicación web del Día 21 del reto [30 Días, 30 Proyectos](../../README.md). Presentará métricas operativas en una vista compacta para detectar tendencias, comparar periodos y consultar el detalle de una serie sin depender de un backend.

**Estado:** Fase 6 completada. El contrato Zod, el fixture local, los cálculos derivados, la interfaz responsive, las visualizaciones, el adaptador de datos, el fallback local, la cobertura de calidad y la documentación de publicación están implementados.

## Problema

Consultar indicadores repartidos entre hojas de cálculo o respuestas de API dificulta saber qué está ocurriendo ahora y qué tendencia está tomando cada métrica. Este proyecto concentra un conjunto pequeño de indicadores en un dashboard visual, legible y usable en escritorio y móvil.

## Objetivo del MVP

Permitir que una persona explore un conjunto de métricas de ejemplo, cambie el periodo visible y entienda rápidamente el estado actual, la variación frente al periodo anterior y la evolución temporal.

## Alcance

- Mostrar una cabecera de dashboard con fecha de última actualización y estado de los datos.
- Presentar tarjetas de KPI con valor actual, variación y dirección de la tendencia.
- Mostrar una serie temporal principal con selección de métrica.
- Mostrar un desglose por categoría o canal.
- Filtrar el periodo visible con opciones predefinidas.
- Permitir consultar el detalle de puntos de la serie sin abandonar la pantalla.
- Cargar datos desde un fixture local reproducible.
- Mantener la interfaz responsive y navegable con teclado.
- Mostrar estados de carga, vacío y error de datos.

## Fuera de alcance

- Autenticación, cuentas, permisos o colaboración.
- Conexión obligatoria con un proveedor de analítica.
- Backend, base de datos o ingesta en tiempo real.
- Constructor de métricas o editor de consultas.
- Exportación avanzada a PDF, CSV o imágenes.
- Alertas, notificaciones o envío de informes.
- Personalización completa del layout por usuario.
- Predicciones, recomendaciones o análisis generativo.

## Tecnologías previstas

- Next.js con App Router.
- React y TypeScript.
- Tailwind CSS para estilos responsive.
- Recharts para gráficas accesibles y adaptables.
- Zod para validar el contrato de datos del dashboard.
- Vitest y Testing Library para pruebas del modelo y de los flujos principales.
- ESLint y TypeScript en modo estricto.

## Requisitos

- Node.js 20 o superior.
- npm.
- Navegador moderno con JavaScript habilitado.

## Instalación y comandos previstos

```bash
npm install
npm run dev
npm run build
npm run lint
npm test
npm run start
```

La configuración base y los scripts están preparados para la implementación incremental. No se requieren credenciales para validar el contrato ni para ejecutar el MVP cuando se complete la interfaz.

## Experiencia principal

1. La aplicación abre un dashboard con datos de ejemplo y el periodo inicial seleccionado.
2. La persona usuaria revisa los KPI principales y sus variaciones.
3. Cambia el periodo o la métrica de la gráfica.
4. Explora un punto de la serie y compara el desglose por categoría.
5. La interfaz comunica la fecha de actualización y cualquier estado anómalo de los datos.
6. La misma experiencia funciona en una pantalla pequeña sin depender de hover.

## Modelo y reglas

- El dataset tiene una versión y una fecha de actualización.
- El MVP incluye las métricas `active-users`, `conversion-rate`, `monthly-revenue` y `avg-response-time`.
- Los periodos disponibles son `7d`, `30d` y `90d`; el fixture inicia en `30d`.
- La jerarquía visual prevista es: estado y actualización, KPI resumidos, serie temporal principal y desglose por categoría.
- Cada métrica define identificador, nombre, unidad, valor actual, valor anterior y serie temporal.
- Las fechas de la serie se normalizan a un formato estable antes de renderizarse.
- Las variaciones se calculan con el valor actual y el valor de comparación; cuando no existe una base válida se muestra un estado neutral.
- Los valores deben ser finitos y las categorías no pueden tener identificadores duplicados.
- El filtro de periodo solo acepta opciones definidas por el contrato.
- El dashboard no debe presentar datos parcialmente inválidos como si fueran correctos.
- `calculateVariation` devuelve cambio absoluto, porcentaje y dirección (`up`, `down`, `neutral` o `unknown`).
- `selectDashboardView` resuelve la selección activa y entrega la métrica, serie filtrada, desglose y variación desde el mismo dataset.

## Datos, integración y fallback

- **Ruta principal del MVP:** fixture JSON local en `data/metrics-dashboard.json`, validado antes de ser usado.
- **Adaptador disponible:** `createHttpDashboardSource` permite conectar una API JSON sin acoplar la UI al proveedor.
- **Fallback:** el fixture local permite ejecutar y demostrar todo el flujo sin red, cuenta ni credenciales.
- **Criterio de cambio:** si una integración externa no está validada antes de T+30, se conserva el fixture como fuente de la demo.
- No se versionan secretos ni configuraciones reales.

## Decisiones técnicas previstas

- Separar el contrato y las transformaciones de métricas de los componentes de presentación.
- Validar el fixture con Zod para detectar datos corruptos antes de dibujar gráficos.
- Mantener las gráficas como una capa de visualización; los KPI y variaciones se calcularán en funciones testeables.
- Usar controles explícitos para cambiar periodo y métrica, evitando depender solo de interacciones visuales.
- Encapsular el acceso a datos en `loadDashboard`, que valida la fuente principal y vuelve al fixture ante errores de red o contrato.
- Diseñar el dashboard para lectura rápida: jerarquía clara, contraste suficiente y estados vacíos comprensibles.

## Estructura prevista

```text
day-21-dashboard-metrics/
├── README.md
├── ROADMAP.md
├── package.json
├── tsconfig.json
├── next.config.ts
├── postcss.config.mjs
├── src/
│   ├── app/                 # Layout, página y estilos globales de Next.js
│   ├── components/          # KPI cards, gráficas, filtros y estados de pantalla
│   ├── hooks/               # Estado de filtros y carga coordinada
│   └── lib/                 # Tipos, esquemas, cálculos y adaptadores de datos
├── tests/                   # Pruebas de contrato, cálculos y flujos principales
├── data/                    # Fixture local del dashboard
├── assets/                  # Capturas, GIF y recursos de demostración
└── docs/                    # Guion de demo, publicación y revisión final
```

## Validación

- Validar el fixture completo y rechazar métricas incompletas o valores no finitos.
- Comprobar el cálculo de variaciones positivas, negativas, neutras y sin base de comparación.
- Cambiar periodo y métrica sin perder el estado visible ni producir series inconsistentes.
- Verificar estados de carga, vacío y error.
- Comprobar que los KPI no dependen de hover y que las gráficas tienen alternativa textual o tabular.
- Revisar teclado, foco, contraste y responsive en escritorio y móvil.
- La Fase 1 valida el fixture, las fechas, los valores finitos, los IDs duplicados y el periodo por defecto con `npm test`.
- La Fase 2 valida variaciones, selección de métrica y periodo, ventanas temporales y ausencia de mutaciones con `npm test`.
- La Fase 3 se valida con `npm run build` y una revisión manual de escritorio y móvil; el selector de periodo actualiza la ventana visible sin overflow horizontal.
- La Fase 4 se valida con `npm test`, `npm run build` y una revisión manual; el selector de métrica, el detalle del punto y la tabla alternativa representan la misma selección activa.
- La Fase 5 cubre el shell, los estados vacío y de error, el fallback HTTP, el responsive y la calidad estática con `npm test`, `npm run lint` y `npm run build`.
- Ejecutar `npm run lint`, `npm run build` y la suite completa antes de cerrar el proyecto.

## Demo y publicación

La demostración muestra la carga del dashboard, la lectura de los KPI, el cambio de periodo, la selección de otra métrica y la inspección de un punto de la serie en menos de 15 segundos. El guion reproducible está en [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md), el borrador de publicación en [`docs/LINKEDIN_POST.md`](docs/LINKEDIN_POST.md), la revisión de seguridad en [`docs/SECURITY_REVIEW.md`](docs/SECURITY_REVIEW.md) y la referencia visual en [`assets/dashboard-reference.png`](assets/dashboard-reference.png).

Consulta [ROADMAP.md](ROADMAP.md) para el plan de trabajo por fases.
