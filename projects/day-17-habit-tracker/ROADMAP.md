# Hoja de Ruta: Rastreador de Hábitos (Día 17)

Este documento divide el desarrollo del proyecto en 6 fases incrementales para asegurar el cumplimiento del límite rígido de 3 horas diarias.

## Fase 0: Configuración Inicial 
- [x] Inicializar el proyecto con Vite (React + TypeScript).
- [x] Configurar Tailwind CSS para el diseño.
- [x] Crear la estructura de carpetas (`src/components`, `src/hooks`, `src/db`, `src/utils`).
- [x] Redactar el `README.md` y este `ROADMAP.md`.

## Fase 1: Motor de Estado Lógico (Mocks)
- [x] Definir las interfaces TypeScript (`Habit`, `HabitLog`).
- [x] Crear un custom hook `useHabits` con un estado inicial en memoria (`useState`).
- [x] Cargar datos de prueba realistas para facilitar el diseño UI. Ejemplos de hábitos base:
  - *"Sesión de Calistenia (Dominadas/Fondos)"*
  - *"Sprints en pista de atletismo"*
  - *"Bloque de estudio profundo (90 min)"*
  - *"Commit del reto 30 Días"*

## Fase 2: Interfaz de Usuario (UI)
- [x] Diseñar el `HabitList`: Un panel donde se muestren los hábitos activos.
- [x] Desarrollar el `WeeklyGrid`: Botones interactivos tipo "checkbox" para los últimos 7 días.
- [x] Crear el formulario para añadir nuevos hábitos como modal accesible.
- [x] Aplicar diseño con Tailwind (estilo minimalista, gamificación visual para rachas completas).

### Estado actual

La interfaz permite listar hábitos, crear nuevos hábitos y marcar o desmarcar cada uno de los últimos siete días. Los datos se persisten localmente mediante IndexedDB.

## Fase 3: Persistencia Local (IndexedDB)
- [x] Configurar el adaptador de IndexedDB con la librería `idb`.
- [x] Modificar `useHabits` para que el estado se sincronice con la base de datos local del navegador.
- [x] Asegurar que al recargar la página (F5), el estado de los hábitos se mantenga intacto.

### Estado actual

Los hábitos y registros se guardan en IndexedDB. En la primera ejecución se cargan los mocks como datos iniciales; después, la aplicación recupera el snapshot persistido. La persistencia se verificó creando un hábito, recargando la página y confirmando que seguía visible.

> La persistencia y los casos límite se cubrieron en la Fase 5; Redis queda fuera del alcance actual y se conserva como mejora futura.

## Fase 5: Pruebas y Refactorización
- [x] Testear la persistencia (guardar un snapshot, cerrar la sesión de almacenamiento, reabrir y recuperar).
- [x] Testear casos límite: marcar un hábito en un día pasado, eliminar un hábito con historial.
- [x] Pulir accesibilidad de teclado en la UI (Escape para cerrar el modal y roles ARIA de diálogo).

### Estado actual

La lógica de alternar registros y eliminar hábitos se encuentra extraída en operaciones puras y cubierta con Vitest. IndexedDB se prueba con `fake-indexeddb`, y la eliminación limpia también el historial asociado. La aplicación expone `npm test` para ejecutar la suite completa.

## Fase 6: Documentación y Demo
- [ ] Grabar el vídeo/GIF demostrativo de 15 segundos marcando hábitos.
- [x] Documentar el uso de IndexedDB y el fallback local en el `README.md`.
- [x] Redactar el post para LinkedIn destacando el patrón *offline-first*.

### Estado actual

La documentación técnica y el borrador de comunicación están preparados. El único pendiente de esta fase es capturar el GIF siguiendo el guion de `docs/DEMO_SCRIPT.md`.

## Mejoras futuras

### Sincronización opcional en la nube con Redis

- [ ] Crear un servicio `redisSync.ts`.
- [ ] Implementar la subida del JSON de hábitos a una instancia de Redis configurada (por ejemplo, Upstash REST API).
- [ ] Aplicar un fallback para que un error remoto no interrumpa el uso local con IndexedDB.