# Borrador de publicación

## Dashboard de métricas operativas sin ruido

En el Día 21 del reto construí un dashboard local para leer el estado de una operación en pocos segundos.

El problema era habitual: los indicadores viven repartidos entre hojas, respuestas de API y gráficas difíciles de comparar. La solución concentra cuatro señales en una vista clara: usuarios activos, conversión, ingresos del mes y tiempo medio de respuesta.

El MVP permite:

- Consultar KPI con valor actual, variación y dirección de tendencia.
- Cambiar la ventana de análisis entre 7, 30 y 90 días.
- Explorar la evolución temporal de cada métrica.
- Comparar el desglose por categoría.
- Consultar los mismos datos en una tabla accesible.
- Continuar la demo con un fixture local aunque falle una fuente HTTP.

La decisión técnica principal fue separar el contrato validado, los cálculos derivados y la presentación. `loadDashboard` valida cualquier fuente antes de usarla y vuelve al fixture local ante errores de red o datos corruptos.

El resultado es una aplicación reproducible: no necesita cuentas, credenciales ni backend para demostrar el flujo. La suite cubre el modelo, las interacciones, los estados vacíos y el fallback; ESLint y el build de producción también pasan.

Código y demo local: [`projects/day-21-dashboard-metrics`](../)

#NextJS #React #TypeScript #Recharts #Zod #Frontend #Accessibility #30Dias30Proyectos
