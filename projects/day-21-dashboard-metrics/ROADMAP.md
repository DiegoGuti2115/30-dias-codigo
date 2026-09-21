# Hoja de Ruta: Dashboard de métricas (Día 21)

El desarrollo se divide en incrementos pequeños para respetar el límite de tres horas del reto. Las Fases 0 a 6 cubren el alcance, el contrato, el modelo derivado, la pantalla usable, la exploración visual, la calidad de ejecución y la publicación reproducible.

## Fase 0: Alcance y estructura

- [x] Crear la carpeta `projects/day-21-dashboard-metrics`.
- [x] Redactar `README.md` con problema, alcance, reglas y fallback.
- [x] Redactar este `ROADMAP.md`.
- [x] Reservar `src`, `tests`, `data`, `assets` y `docs`.
- [x] Reservar `src/app`, `src/components`, `src/hooks` y `src/lib`.
- [x] Fijar un MVP basado en fixture local sin credenciales.
- [x] Confirmar la jerarquía visual y las métricas definitivas antes de implementar.

**Criterio de salida:** el problema, el contrato inicial y la estructura de trabajo están definidos sin incluir una implementación funcional.

**Estado:** Fase completada. La jerarquía visual queda definida como estado y actualización, KPI, serie temporal y desglose. El MVP usa `active-users`, `conversion-rate`, `monthly-revenue` y `avg-response-time` con periodos `7d`, `30d` y `90d`.

## Fase 1: Contrato de datos y fixture

- [x] Definir los tipos de dashboard, métrica, punto temporal y desglose.
- [x] Definir el esquema Zod del dataset versionado.
- [x] Definir unidades, periodos soportados y estados de calidad del dato.
- [x] Preparar `data/metrics-dashboard.json` con datos de demostración realistas.
- [x] Implementar normalización de fechas y orden de series.
- [x] Cubrir datos válidos, vacíos, incompletos y corruptos.

**Criterio de salida:** el fixture puede cargarse y validarse sin depender de React, Next.js ni la red.

**Estado:** Fase completada. `src/lib/types.ts`, `src/lib/schema.ts` y `src/lib/normalize.ts` definen y validan el contrato. El fixture local contiene cuatro métricas, tres periodos y desgloses por canal o categoría; `npm test` pasa 9 pruebas.

## Fase 2: Cálculos y estado del dashboard

- [x] Implementar el cálculo de variación absoluta y porcentual.
- [x] Resolver el caso sin valor de comparación y valores iguales.
- [x] Implementar selección de periodo y métrica.
- [x] Derivar KPI, serie y desglose desde una única fuente validada.
- [x] Cubrir las funciones puras con pruebas unitarias.

**Criterio de salida:** el modelo produce resultados consistentes para todos los estados del MVP sin mutar el dataset original.

**Estado:** Fase completada. `src/lib/dashboard.ts` expone `calculateVariation` y `selectDashboardView`; la suite cubre cambios ascendentes, descendentes, neutros, sin base válida, selección de métrica y periodo, ventanas temporales, errores de selección y ausencia de mutaciones. `npm test` pasa 17 pruebas.

## Fase 3: Layout y KPI

- [x] Crear el layout principal con App Router.
- [x] Construir la cabecera con título, periodo y última actualización.
- [x] Construir tarjetas de KPI con valor, unidad, variación y tendencia.
- [x] Añadir estados de carga, vacío y error.
- [x] Revisar jerarquía, contraste, foco y lectura en móvil.

**Criterio de salida:** una persona puede abrir el dashboard y entender el estado general sin interactuar con una gráfica.

**Estado:** Fase completada. `src/app` contiene el layout, la página, los estilos globales y los estados de App Router. `DashboardShell` presenta la cabecera, el selector de periodo, cuatro KPI y el estado de calidad; la revisión local confirmó cambio de periodo y ausencia de overflow en móvil. `npm run build` pasa.

## Fase 4: Visualizaciones e interacción

- [x] Añadir la gráfica temporal principal.
- [x] Añadir selector accesible de métrica.
- [x] Añadir desglose por categoría o canal.
- [x] Mostrar tooltip y detalle del punto seleccionado.
- [x] Añadir una alternativa tabular o textual para los datos de la gráfica.
- [x] Evitar que hover sea el único mecanismo para descubrir información.

**Criterio de salida:** la persona puede cambiar el foco del análisis y comparar la evolución temporal con el desglose.

**Estado:** Fase completada. `MetricAnalysis` integra Recharts, selector de métrica con `aria-pressed`, detalle persistente del último punto seleccionado, desglose proporcional y tabla accesible de la serie. La revisión local confirmó cambio de métrica, actualización del desglose, tabla con 7 filas y ausencia de overflow en móvil. `npm test` pasa 19 pruebas y `npm run build` pasa.

## Fase 5: Calidad, responsive y datos externos opcionales

- [x] Cubrir el flujo principal con pruebas de componentes.
- [x] Comprobar filtros, estados vacíos y errores de validación.
- [x] Revisar teclado, foco, semántica y contraste.
- [x] Revisar escritorio, tablet y móvil sin overflow horizontal.
- [x] Encapsular una fuente HTTP detrás de un adaptador.
- [x] Mantener el fixture como fallback cuando la fuente externa falle.
- [x] Ejecutar lint, build y la suite completa.

**Criterio de salida:** la aplicación funciona de forma reproducible con datos locales y mantiene una experiencia clara en los tamaños objetivo.

**Estado:** Fase completada. `src/lib/dataSource.ts` valida cualquier fuente y recupera el fixture local ante errores HTTP o datos inválidos. Las pruebas cubren fuente remota correcta, error 503, contrato corrupto, cambio de periodo y estado vacío. La revisión responsive no detectó overflow horizontal; `npm test` pasa 24 pruebas, `npm run lint` pasa y `npm run build` pasa.

## Fase 6: Documentación, demo y publicación

- [x] Redactar `docs/DEMO_SCRIPT.md` con una demo reproducible de 15 segundos.
- [x] Capturar una referencia visual del dashboard.
- [x] Redactar `docs/LINKEDIN_POST.md` con problema, decisiones y fallback.
- [x] Actualizar `README.md` con comandos y estado real.
- [x] Confirmar que no hay secretos ni archivos de entorno reales.
- [x] Actualizar el registro raíz con enlaces de código y demo.

**Criterio de salida:** el proyecto puede instalarse, validarse, demostrarse y publicarse siguiendo instrucciones limpias.

**Estado:** Fase completada. El guion de demo, la captura `assets/dashboard-reference.png`, el borrador de LinkedIn y la revisión de seguridad están disponibles. README y registro raíz enlazan el código y los recursos de publicación; la auditoría no encontró secretos en los archivos revisados.

## Criterios de terminado

- El dashboard carga un dataset validado y reproducible.
- Los KPI muestran valores y variaciones correctos.
- El periodo y la métrica se pueden cambiar con controles accesibles.
- La serie temporal y el desglose representan la misma selección activa.
- Existen estados claros de carga, vacío y error.
- La información importante no depende exclusivamente de color, hover o animación.
- El fallback local permite demostrar el proyecto sin red ni credenciales.
- La interfaz funciona en escritorio y móvil.
- `npm run lint`, `npm run build` y `npm test` pasan.
- `README.md` permite instalar, ejecutar, validar y entender las decisiones del proyecto.

## Mejoras futuras

- Comparación entre dos segmentos seleccionables.
- Persistencia local de la última vista y filtros.
- Exportación de la vista a CSV.
- Configuración de umbrales y alertas locales.
- Fuente HTTP con caché y actualización manual.
- Personalización limitada de widgets sin convertirlo en un constructor.
