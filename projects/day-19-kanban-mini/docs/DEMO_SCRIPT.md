# Guion de demo — Kanban mínimo

Duración objetivo: 15 segundos.

## Preparación

- Ejecutar `npm run dev` desde `projects/day-19-kanban-mini`.
- Abrir la URL local indicada por Vite.
- Usar un tablero limpio con las cuatro tarjetas del fixture.
- Mantener visible el tablero completo en un viewport de escritorio o grabar en formato vertical de 390 px.

## Secuencia

| Tiempo | Acción | Resultado visible |
|---|---|---|
| 0-2 s | Mostrar el tablero inicial. | Tres columnas, contadores y tarjetas distribuidas. |
| 2-5 s | Pulsar `Nueva tarea`. | Se abre el formulario con foco en `Título`. |
| 5-7 s | Escribir `Preparar demo` y una descripción breve; pulsar `Añadir tarjeta`. | La tarjeta aparece en `Por hacer`. |
| 7-10 s | Cambiar el selector `Mover a` de la tarjeta a `En progreso`. | La tarjeta cambia de columna y el contador se actualiza. |
| 10-12 s | Cambiar el selector a `Completado`. | La tarjeta llega a la tercera columna. |
| 12-15 s | Recargar la página y mostrar la cabecera `Guardado en este navegador`. | La tarjeta permanece gracias a IndexedDB. |

## Alternativa de fallback

Si el navegador no permite IndexedDB:

1. Mostrar el aviso de modo memoria.
2. Crear y mover la tarjeta de la misma forma.
3. No incluir la recarga en la grabación, porque los cambios solo duran durante la sesión.

## Criterios de captura

- No mostrar credenciales, rutas personales ni otras pestañas.
- Mantener el puntero fuera de los textos importantes.
- Grabar una sola secuencia continua, sin acelerar la interacción.
- El resultado final debe mostrar la tarjeta en `Completado` y el estado de almacenamiento.
