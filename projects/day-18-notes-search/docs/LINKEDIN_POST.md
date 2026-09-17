# Borrador para LinkedIn

## Día 18 de 30: Buscador de notas offline-first

Hoy construí un buscador de notas local con React, TypeScript, Vite e IndexedDB.

La herramienta permite:

- Crear, editar y eliminar notas.
- Buscar en títulos, contenido y etiquetas.
- Combinar texto de búsqueda con filtros por etiqueta.
- Ordenar por fecha o título.
- Mantener los datos después de recargar la página.
- Continuar funcionando en memoria si IndexedDB no está disponible.

La decisión técnica principal fue separar el motor de búsqueda y el almacenamiento de la interfaz. La búsqueda es pura y determinista; el adaptador `idb` encapsula IndexedDB; y el hook `useNotes` coordina hidratación, operaciones CRUD y fallback local.

El MVP no usa backend, cuentas ni servicios externos. Así la aplicación puede funcionar offline y el comportamiento crítico se puede probar de forma reproducible con Vitest y `fake-indexeddb`.

La validación final incluye 15 pruebas automatizadas, lint, build de producción y comprobaciones responsive en escritorio y móvil.

Demo: [añadir enlace al GIF o vídeo]

Código: [añadir enlace al repositorio]

#30DiasDeCodigo #React #TypeScript #IndexedDB #Frontend #OfflineFirst