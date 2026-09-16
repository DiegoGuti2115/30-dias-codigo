# Guion de demo

## Objetivo

Capturar un GIF o vídeo de aproximadamente 15 segundos que muestre el flujo principal del rastreador sin depender de servicios externos.

## Preparación

1. Ejecuta `npm run dev` desde la carpeta del proyecto.
2. Abre la URL local que muestre Vite.
3. Usa una ventana limpia del navegador o conserva los datos locales si quieres mostrar la persistencia.
4. Ajusta la ventana para que se vean el encabezado y varias tarjetas de hábitos.

## Secuencia de 15 segundos

- **0-3 s:** Mostrar el listado inicial de hábitos.
- **3-6 s:** Pulsar un día vacío en la cuadrícula de un hábito.
- **6-8 s:** Mostrar el día marcado visualmente.
- **8-11 s:** Abrir `+ Nuevo Hábito` y crear un hábito breve, por ejemplo `Leer 20 minutos`.
- **11-13 s:** Mostrar el nuevo hábito en la lista.
- **13-15 s:** Recargar la página y mostrar que el hábito sigue presente gracias a IndexedDB.

## Criterios de salida

- La grabación dura entre 12 y 18 segundos.
- El texto de los controles se puede leer.
- Se ve al menos una marca de cumplimiento, un alta y la persistencia tras recargar.
- No aparecen credenciales, rutas privadas ni datos personales.

La grabación es el único entregable manual pendiente de la Fase 6.
