# Hoja de Ruta: Buscador de Notas (Día 18)

El desarrollo se divide en seis fases incrementales para mantener el límite de tres horas del reto y conservar una entrega funcional en cada paso.

## Fase 0: Configuración y contrato

- [x] Inicializar el proyecto con Vite, React y TypeScript.
- [x] Configurar Tailwind CSS, ESLint y Vitest.
- [x] Crear la estructura de carpetas del proyecto.
- [x] Redactar `README.md` y `ROADMAP.md`.
- [x] Definir los scripts de instalación, desarrollo, compilación, lint y pruebas.

## Fase 1: Modelo y datos de prueba

- [x] Definir el modelo `Note` con identificador, título, contenido, etiquetas y fechas; el archivado queda fuera del MVP.
- [x] Definir los tipos de consulta, filtro y ordenación.
- [x] Preparar fixtures realistas de notas en `data/`.
- [x] Crear las funciones puras para normalizar texto y extraer etiquetas.
- [x] Acordar reglas para títulos vacíos, contenido vacío y etiquetas duplicadas.

## Fase 2: Motor de búsqueda

- [x] Implementar búsqueda por título, contenido y etiquetas.
- [x] Ignorar mayúsculas, minúsculas y espacios innecesarios.
- [x] Implementar filtro por etiqueta.
- [x] Implementar ordenación por última actualización.
- [x] Componer búsqueda, filtro y ordenación sin mutar la colección original.
- [x] Cubrir coincidencias, ausencia de resultados y consultas vacías con pruebas.

## Fase 3: Interfaz de usuario

- [x] Diseñar el layout responsive de la aplicación.
- [x] Crear la barra de búsqueda y el selector de etiquetas.
- [x] Crear la lista de resultados con título, extracto, etiquetas y fecha.
- [x] Crear el panel de detalle y el formulario de alta/edición.
- [x] Añadir acciones de guardar, cancelar y eliminar.
- [x] Diseñar estados de colección vacía y búsqueda sin resultados.
- [x] Revisar navegación básica de teclado, foco y nombres accesibles.

## Fase 4: Persistencia local

- [x] Configurar IndexedDB mediante `idb`.
- [x] Implementar lectura, creación, actualización y eliminación de notas.
- [x] Hidratar la aplicación desde el almacenamiento local al iniciar.
- [x] Cargar los fixtures solo cuando la base de datos esté vacía.
- [x] Añadir fallback en memoria cuando IndexedDB no exista o falle.
- [x] Confirmar que una recarga conserva las notas y su ordenación.

**Estado:** Fase completada. La aplicación hidrata las notas desde IndexedDB, persiste las operaciones CRUD y conserva un fallback en memoria cuando el almacenamiento local no está disponible.

## Fase 5: Pruebas y pulido

- [x] Probar la persistencia tras cerrar y reabrir la conexión.
- [x] Probar búsqueda combinada con filtro de etiqueta.
- [x] Probar edición y eliminación sin perder otras notas.
- [x] Probar el fallback local ante un error de IndexedDB.
- [x] Validar responsive en viewport móvil y escritorio.
- [x] Ejecutar lint, build y suite completa de pruebas.
- [x] Corregir detalles de accesibilidad y estados de interacción.

**Estado:** Fase completada. La suite cubre búsqueda combinada, persistencia tras reapertura, CRUD sin pérdida de notas y fallback en memoria; la interfaz fue revisada en escritorio y móvil.

## Fase 6: Documentación y demo

- [x] Redactar un guion de demo de 15 segundos en `docs/DEMO_SCRIPT.md`.
- [x] Capturar una demostración creando una nota y encontrándola mediante búsqueda.
- [x] Documentar la persistencia IndexedDB y el fallback en la documentación final.
- [x] Preparar el borrador de publicación en `docs/LINKEDIN_POST.md`.
- [x] Actualizar el estado final del proyecto y los pendientes reales.

**Estado:** Fase completada. El proyecto dispone de un guion reproducible de demo, documentación de arquitectura y fallback, y un borrador listo para publicar.

## Criterios de terminado

- La aplicación permite crear, editar, eliminar y encontrar notas sin recargar.
- La búsqueda cubre título, contenido y etiquetas y distingue correctamente los estados sin resultados.
- Los datos sobreviven a una recarga cuando IndexedDB está disponible.
- La interfaz continúa siendo utilizable en memoria cuando IndexedDB no está disponible.
- Las operaciones de negocio y persistencia tienen pruebas reproducibles.
- El proyecto se puede instalar, probar y compilar siguiendo el `README.md`.

## Mejoras futuras

- Atajos de teclado para abrir el buscador y crear una nota.
- Resaltado de coincidencias en título y contenido.
- Archivado y papelera con recuperación.
- Exportación e importación de notas en JSON.
- Sincronización remota opcional con autenticación y resolución de conflictos.