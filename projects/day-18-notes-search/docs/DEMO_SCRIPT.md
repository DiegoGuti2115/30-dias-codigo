# Guion de Demo: Buscador de Notas

Duración objetivo: 15 segundos.

## Preparación

1. Ejecutar `npm run dev` desde `projects/day-18-notes-search`.
2. Abrir la URL local mostrada por Vite.
3. Confirmar que aparece `Guardado local` y que se muestran las notas iniciales.

## Secuencia

| Tiempo | Acción | Resultado visible |
| :---: | :--- | :--- |
| 0-3 s | Pulsar `Nueva nota`. | Se abre el formulario de edición con foco en el título. |
| 3-7 s | Escribir `Reunión de arquitectura`, contenido breve y las etiquetas `equipo, arquitectura`. | El formulario queda listo para guardar. |
| 7-9 s | Pulsar `Guardar nota`. | La nota aparece en la lista y queda seleccionada. |
| 9-12 s | Escribir `arquitectura` en el buscador. | La lista se filtra al instante por el texto de la nota y sus etiquetas. |
| 12-15 s | Recargar la página. | La nota sigue visible y el indicador confirma `Guardado local`. |

## Narración sugerida

> Creo una nota, la etiqueto y la guardo. El buscador encuentra la información al instante en título, contenido o etiquetas. Todo queda guardado en el navegador y sigue disponible después de recargar, incluso sin backend.

## Comprobación alternativa

Para mostrar el fallback, abrir la aplicación en un entorno sin IndexedDB. La cabecera cambiará a `Modo memoria` y aparecerá un aviso indicando que los cambios solo vivirán durante la sesión.