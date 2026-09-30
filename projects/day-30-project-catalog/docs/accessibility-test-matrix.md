# Matriz de pruebas manuales de accesibilidad

## Propósito

Esta matriz verifica el flujo principal del Catálogo de proyectos sin depender de red: cargar la colección local, buscar, combinar filtros y restablecer criterios. La apertura de **Código** navega al repositorio público de GitHub y debe comprobarse con conectividad. Debe ejecutarse antes de una demostración o cuando cambien los controles, los estados o los estilos globales.

## Entorno recomendado

- Ejecutar `npm run dev` y abrir la ruta raíz.
- Probar los viewports de 320 px, 768 px y 1280 px de ancho.
- Probar al menos Chrome o Edge en Windows y un navegador adicional cuando esté disponible.
- Activar `prefers-reduced-motion: reduce` en las herramientas de desarrollo para la comprobación de movimiento.
- Para la revisión con lector de pantalla, usar Narrador de Windows, NVDA o VoiceOver según el entorno disponible.

## Matriz

| Área | Procedimiento | Resultado esperado |
| --- | --- | --- |
| Teclado inicial | Recargar la página y pulsar Tab una vez. Pulsar Intro en «Saltar al contenido principal». | El enlace de salto es visible al recibir foco y mueve el foco al contenido principal. |
| Orden de foco | Recorrer cabecera, buscador, selectores, restablecimiento y enlaces de tarjetas solo con Tab y Shift+Tab. | El orden sigue la lectura visual; ningún control queda inaccesible ni atrapado. |
| Búsqueda | Con foco en «Buscar proyectos», escribir un término que deje un único resultado. | El texto de ayuda explica la actualización y el contador anuncia el nuevo número de proyectos. |
| Filtros nativos | Con teclado, cambiar categoría y tecnología en los selectores. | Ambos controles conservan el foco, se pueden operar con las teclas nativas y combinan criterios. |
| Restablecimiento | Aplicar uno o varios criterios, activar «Restablecer criterios» y comprobar su estado antes y después. | Está deshabilitado sin criterios, vuelve a mostrar 30 proyectos y limpia los tres controles. |
| Sin resultados | Buscar un término sin coincidencias. Activar «Ver todos los proyectos». | Se comunica el estado sin depender del color y la acción recupera la colección completa. |
| Enlaces de proyecto | Llegar a un enlace «Código» con Tab y activarlo con Intro. | El foco es claramente visible, el objetivo táctil es cómodo y el destino es el directorio correspondiente en el monorepo público de GitHub. |
| Estados de error | Forzar o renderizar los estados de error disponibles durante desarrollo. | Cada estado tiene encabezado, explicación no técnica y acción de recuperación accesible. |
| Lector de pantalla | Recorrer landmarks, encabezados, controles y resultados con el lector de pantalla. | Se anuncian main, las etiquetas de controles, la ayuda, el contador, la región de resultados y los recursos de cada tarjeta. |
| Móvil y zoom | Revisar a 320 px y con zoom de navegador al 200 %. | No aparece desplazamiento horizontal, el contenido no se solapa y todos los controles siguen utilizables. |
| Movimiento | Activar reducción de movimiento y cambiar filtros. | Las animaciones y transiciones se reducen; el contenido sigue siendo comprensible. |
| Color y contraste | Revisar texto, bordes, foco, botones deshabilitados y estado de error. | La información relevante no depende solo del color y foco/contraste se distinguen con claridad. |

## Registro de incidencias

Registrar cualquier barrera con: fecha, navegador, viewport, tecnología de asistencia, pasos para reproducir, resultado observado, severidad y enlace al cambio correctivo. No dar por completada una revisión si una incidencia crítica bloquea búsqueda, filtros, recuperación o apertura de recursos.