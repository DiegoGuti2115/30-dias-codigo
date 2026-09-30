# Borrador de publicación

## Estado de publicación

El Catálogo de proyectos está cerrado y listo para una demostración local de producción verificable en [http://localhost:3000](http://localhost:3000) tras ejecutar `npm run build && npm run start`. No existe URL pública porque este entorno no dispone de cuenta ni permisos de hosting. La configuración de producción, cabeceras y checklist están en [`deployment.md`](deployment.md).

## Texto breve

> Catálogo de proyectos es el cierre de **30 Días, 30 Proyectos**: una interfaz en Next.js para explorar las 30 entregas mediante búsqueda y filtros accesibles. El catálogo funciona con un fixture local validado, sin servicios externos ni credenciales, y cada enlace **Código** lleva al directorio correspondiente del monorepo público de GitHub.

## Puntos para acompañar la publicación

- Búsqueda por texto y filtros combinables de categoría y tecnología.
- Accesibilidad desde el flujo principal: teclado, foco visible, anuncios de resultados, estados recuperables y reducción de movimiento.
- Validación Zod de estructura, categorías, metadatos locales y destinos restringidos al monorepo de GitHub antes del renderizado.
- Estado de carga, errores recuperables y fallback local determinista.
- Build estática de la ruta principal: 4.9 kB de JavaScript de ruta y 107 kB de First Load JS compartido en la referencia local de Fase 8.

## Checklist para capturas o GIF

1. Usar datos locales y un navegador sin extensiones que alteren el contenido.
2. Capturar la vista inicial con la colección completa y el contador de 30 proyectos.
3. Capturar una búsqueda con un solo resultado y el estado sin coincidencias con su recuperación.
4. Mostrar foco visible o el enlace de salto en al menos una captura si se comunica accesibilidad.
5. No incluir tokens, rutas personales, herramientas de desarrollo, datos privados ni recursos de terceros sin permiso.
6. Guardar recursos finales optimizados en [`assets/`](../assets/) y enlazarlos desde el README solo cuando existan.

## Checklist antes de publicar

- Ejecutar [`quality-verification.md`](quality-verification.md).
- Completar la revisión manual de [`accessibility-test-matrix.md`](accessibility-test-matrix.md).
- Revisar [`performance-and-polish.md`](performance-and-polish.md) en dispositivo o emulación limitada.
- Confirmar que todos los enlaces **Código** resuelven en el directorio correspondiente de [`DiegoGuti2115/30-dias-codigo`](https://github.com/DiegoGuti2115/30-dias-codigo).
- Elegir hosting compatible con Next.js sin convertirlo en requisito para la demo local.
- Registrar la URL pública, la plataforma y la verificación de cabeceras si se crea un despliegue externo.

## Limitaciones que deben comunicarse con precisión

- El catálogo no usa una API remota; el contenido procede del fixture local incluido en el repositorio.
- `repositoryPath` conserva la referencia local del checkout, mientras que **Código** usa una URL HTTPS validada hacia el directorio del proyecto en el monorepo público de GitHub.
- La verificación automatizada no sustituye una revisión final con lector de pantalla y contraste en navegador real.
