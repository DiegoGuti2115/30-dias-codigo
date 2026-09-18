# Borrador para LinkedIn — Día 19

## Texto

Día 19 de 30: construí un Kanban mínimo para hacer visible el siguiente paso.

El problema era sencillo: una lista plana de tareas no muestra con claridad qué está pendiente, qué está en progreso y qué ya terminó. La solución fue un tablero pequeño con tres columnas fijas:

- Por hacer
- En progreso
- Completado

La parte más importante no fue dibujar las columnas, sino mantener las reglas fuera de la interfaz. Las operaciones de crear, editar, mover, eliminar y normalizar posiciones son funciones puras y están cubiertas con pruebas. React solo coordina el estado y presenta las acciones mediante controles accesibles, sin depender de drag and drop para completar el flujo principal.

La persistencia usa IndexedDB a través de `idb`. Si el navegador no ofrece IndexedDB o una escritura falla, la aplicación cambia a modo memoria y mantiene la sesión utilizable. La demo no depende de credenciales, backend ni conexión de red.

Stack: React, TypeScript, Vite, IndexedDB, Vitest y ESLint.

Validación de esta entrega: 20 pruebas, lint, compilación TypeScript y revisión responsive en escritorio y móvil.

Código: `projects/day-19-kanban-mini`

#30Dias30Proyectos #React #TypeScript #Frontend #IndexedDB #SoftwareEngineering

## Notas de publicación

- Adjuntar la demo siguiendo `docs/DEMO_SCRIPT.md`.
- Sustituir la ruta local por la URL pública del repositorio al publicar.
- Mantener el texto del post por debajo del límite de tres horas del reto: problema, decisión técnica, fallback y evidencia.
