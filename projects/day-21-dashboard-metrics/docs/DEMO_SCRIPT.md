# Guion de demo: Dashboard de métricas

Duración objetivo: 15 segundos.

## Preparación

```bash
npm install
npm run dev
```

Abrir la URL local que muestre Next.js. El dashboard usa el fixture de `data/metrics-dashboard.json`, por lo que no requiere credenciales, red ni configuración adicional.

## Secuencia

1. **0-3 s:** mostrar Signal Desk con la fecha de actualización, el estado de datos locales y las cuatro tarjetas KPI.
2. **3-6 s:** cambiar `Ventana de análisis` de `Últimos 30 días` a `Últimos 7 días`; mostrar que el contexto del periodo se actualiza.
3. **6-9 s:** pulsar `Conversión` en el selector de métrica; mostrar el cambio de la serie y del desglose por categoría.
4. **9-12 s:** abrir `Ver datos de la serie en tabla` y mostrar las siete filas con el último punto marcado como `Seleccionado`.
5. **12-15 s:** reducir la ventana a móvil o mostrar la captura de referencia para cerrar con la interfaz completa sin overflow.

## Resultado esperado

- La vista presenta KPI, serie temporal y desglose para la misma selección activa.
- El punto seleccionado permanece visible sin depender del hover.
- La tabla ofrece una alternativa textual y accesible a la gráfica.
- La experiencia funciona con datos locales sin secretos ni servicios externos.

## Fallback de demo

Si se prueba una fuente HTTP opcional y responde con error o datos inválidos, `loadDashboard` recupera y valida automáticamente `data/metrics-dashboard.json`. La demo continúa sin red ni credenciales.

## Evidencia

- Captura de referencia: [`assets/dashboard-reference.png`](../assets/dashboard-reference.png).
- Validación reproducible: `npm test`, `npm run lint` y `npm run build`.
