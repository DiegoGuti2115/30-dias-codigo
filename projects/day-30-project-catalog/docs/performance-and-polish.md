# Rendimiento y pulido

## Línea base medida

La compilación de producción de la Fase 8 mantiene una única ruta estática y no incorpora dependencias nuevas:

| Ruta | JavaScript de la ruta | First Load JS |
| --- | ---: | ---: |
| `/` | 4.85 kB | 107 kB |

La medición se obtiene con `npm run build` en el entorno local del proyecto. Es una referencia de regresión, no una métrica de red real: el tamaño final puede variar con una actualización de Next.js, React o el compilador.

## Decisiones aplicadas

- La colección sigue siendo un fixture local validado y se renderiza de forma estática; no hay solicitudes de red, imágenes remotas ni dependencias externas que retrasen el flujo principal.
- [`CatalogBrowser`](../src/features/catalog/catalog-browser.tsx) difiere el cálculo de resultados durante la escritura mediante `useDeferredValue`, de modo que el campo conserva prioridad de interacción si la colección crece. La región de resultados comunica `aria-busy` durante esa transición.
- Las tarjetas usan `content-visibility: auto` y un tamaño intrínseco estimado. El navegador puede posponer el trabajo de pintado de tarjetas fuera del viewport sin provocar saltos de diseño relevantes.
- [`loading.tsx`](../src/app/loading.tsx) ofrece un estado de carga de App Router con tres previews estáticos, un encabezado y un mensaje anunciado. No bloquea la navegación ni introduce animación obligatoria.
- Las transiciones de tarjeta solo se aplican en dispositivos con hover disponible. La preferencia de reducción de movimiento existente sigue anulando animaciones y transiciones.
- Los metadatos describen el catálogo real y permiten indexación normal. No se añaden imágenes de Open Graph porque el proyecto no cuenta todavía con recursos de demo optimizados; crearlas corresponde a la fase documental.

## Comprobación en dispositivos limitados

Antes de publicar, revisar manualmente:

1. Abrir el catálogo con emulación móvil y throttling de red/CPU en herramientas de desarrollo.
2. Confirmar que el estado de carga se entiende, que el campo de búsqueda responde y que los filtros siguen siendo utilizables.
3. Recorrer la colección con scroll, comprobar que no hay desplazamiento horizontal ni saltos de contenido perceptibles.
4. Activar `prefers-reduced-motion: reduce` y confirmar que el contenido conserva claridad sin depender de transiciones.
5. Repetir los escenarios de teclado y lector de pantalla descritos en [`accessibility-test-matrix.md`](accessibility-test-matrix.md).

Estas verificaciones complementan las pruebas automatizadas; la aplicación no depende de red para completarlas.
