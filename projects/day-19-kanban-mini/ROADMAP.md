# Hoja de Ruta: Kanban Mínimo (Día 19)

El desarrollo se divide en fases pequeñas para mantener el límite de tres horas diarias y conservar una entrega demostrable al final de cada etapa.

## Fase 0: Alcance y estructura

- [x] Crear la carpeta `projects/day-19-kanban-mini`.
- [x] Redactar `README.md` con problema, alcance, reglas y fallback.
- [x] Redactar este `ROADMAP.md`.
- [x] Reservar las carpetas `src`, `tests`, `data`, `assets` y `docs`.
- [x] Reservar las subcarpetas `src/components`, `src/db`, `src/hooks` y `src/utils`.

**Criterio de salida:** el MVP está acotado y la estructura permite comenzar la implementación sin introducir backend ni integraciones externas.

## Fase 1: Modelo y datos de prueba

- [x] Definir los tipos `Board`, `Column`, `Card` y las acciones del tablero.
- [x] Fijar las columnas del MVP: `todo`, `in-progress` y `done`.
- [x] Definir las reglas de título obligatorio, descripción opcional, identificadores y orden.
- [x] Preparar un fixture realista en `data/` con tarjetas distribuidas en las tres columnas.
- [x] Crear funciones puras para añadir, editar, mover, eliminar y reordenar tarjetas.
- [x] Decidir cómo se normalizan espacios, posiciones y valores inválidos.

**Estado:** Fase completada. El modelo y sus operaciones puras están implementados en `src/utils/`, el fixture vive en `data/board.json` y la suite cubre las reglas principales sin depender de React ni del navegador.

**Criterio de salida:** las operaciones del tablero pueden probarse con datos puros, sin depender de React ni del navegador.

## Fase 2: Estado y núcleo de interacción

- [x] Crear el hook que exponga el estado del tablero y sus acciones.
- [x] Hidratar el estado inicial desde el fixture local.
- [x] Implementar creación y edición con validación del título.
- [x] Implementar movimiento entre columnas mediante acciones explícitas.
- [x] Implementar eliminación con confirmación o una interacción equivalente que evite borrados accidentales.
- [x] Mantener el orden estable después de cada operación.

**Estado:** Fase completada. `useBoard` hidrata una copia del fixture, coordina las acciones mediante `useReducer`, expone errores de validación y requiere confirmar o cancelar las eliminaciones pendientes. Las pruebas cubren el flujo local completo.

**Criterio de salida:** el flujo completo funciona en estado local y ninguna acción rompe la colección de tarjetas.

## Fase 3: Interfaz del tablero

- [x] Construir el layout responsive del tablero.
- [x] Crear `Board`, `BoardColumn`, `TaskCard` y el formulario de tarjeta.
- [x] Mostrar contadores y estados vacíos por columna.
- [x] Añadir controles accesibles para editar, eliminar y mover tarjetas.
- [x] Mantener la navegación por teclado, el foco y los nombres de botones comprensibles.
- [x] Diferenciar visualmente las columnas sin sacrificar legibilidad.
- [x] Revisar el comportamiento en móvil, donde las columnas pueden apilarse verticalmente.

**Estado:** Fase completada. La aplicación Vite/React ofrece un tablero responsive con alta, edición, movimiento mediante controles explícitos, estados vacíos y confirmación accesible antes de eliminar. El flujo fue comprobado en escritorio y en un viewport móvil de 390 px.

**Criterio de salida:** una persona puede gestionar un tablero completo desde el navegador sin editar datos manualmente.

## Fase 4: Persistencia local y fallback

- [x] Crear el adaptador de IndexedDB detrás de una API pequeña.
- [x] Guardar y recuperar el snapshot del tablero.
- [x] Cargar el fixture solo cuando no exista un tablero persistido.
- [x] Añadir fallback en memoria si IndexedDB no está disponible o falla.
- [x] Exponer un aviso no bloqueante cuando la aplicación esté en modo memoria.
- [x] Confirmar que crear, editar, mover y eliminar sobreviven a una recarga cuando el almacenamiento está disponible.

**Estado:** Fase completada. `src/db/storage.ts` encapsula IndexedDB con `idb`; `useBoard` hidrata el fixture, persiste cada snapshot y cambia a modo memoria cuando una lectura o escritura falla. La UI comunica el modo activo y las pruebas cubren snapshots, aislamiento de referencias, rehidratación y fallback.

**Criterio de salida:** la aplicación es útil offline y una falla de almacenamiento no impide continuar con la demo.

## Fase 5: Pruebas y pulido

- [x] Probar las operaciones puras del tablero con columnas vacías y múltiples tarjetas.
- [x] Probar validación de títulos y edición sin pérdida de la descripción.
- [x] Probar movimiento entre columnas y conservación del orden.
- [x] Probar eliminación y limpieza de posiciones.
- [x] Probar persistencia tras cerrar y reabrir la conexión.
- [x] Probar el fallback en memoria ante una operación fallida.
- [x] Validar teclado, foco, estados vacíos y responsive.
- [x] Ejecutar lint, build y la suite completa de pruebas.

**Estado:** Fase completada. La suite cubre reglas, estados del hook, persistencia IndexedDB, rehidratación y fallos de lectura/escritura con 20 pruebas. ESLint y TypeScript pasan; la UI fue revisada con foco automático en formularios, cierre por `Escape`, nombres accesibles y ausencia de overflow horizontal en escritorio y móvil.

**Criterio de salida:** el flujo principal y sus casos límite tienen verificaciones reproducibles y la aplicación compila sin errores.

## Fase 6: Documentación, demo y publicación

- [x] Redactar `docs/DEMO_SCRIPT.md` con una demo reproducible de 15 segundos.
- [x] Capturar una referencia visual del tablero y validar el flujo creando y moviendo una tarjeta.
- [x] Redactar `docs/LINKEDIN_POST.md` con el problema, la decisión técnica y el fallback.
- [x] Actualizar el `README.md` con los comandos y el estado real del proyecto.
- [x] Confirmar que no hay secretos ni archivos de entorno reales.
- [x] Marcar como completados únicamente los criterios verificados.

**Estado:** Fase completada. La demo está descrita en `docs/DEMO_SCRIPT.md`, la captura de referencia vive en `assets/kanban-reference.png`, el borrador de publicación está preparado y la revisión de configuración no encontró secretos.

**Criterio de salida:** el proyecto puede instalarse, probarse, demostrarse y enlazarse desde el catálogo principal.

## Criterios de terminado

- El tablero muestra las tres columnas del MVP y sus tarjetas.
- Se pueden crear, editar, mover y eliminar tarjetas.
- El orden se conserva y los estados vacíos son comprensibles.
- La interfaz funciona en escritorio y móvil y es navegable con teclado.
- Los datos persisten localmente cuando IndexedDB está disponible.
- El modo memoria mantiene la aplicación utilizable cuando IndexedDB falla.
- Las reglas de negocio, la persistencia y los casos importantes tienen pruebas.
- `README.md` permite instalar, ejecutar y validar el proyecto.

## Mejoras futuras

- Arrastrar y soltar con soporte completo de teclado y puntero.
- Reordenación dentro de una misma columna.
- Etiquetas, prioridades y fechas límite.
- Filtros y búsqueda de tarjetas.
- Varios tableros y columnas personalizables.
- Exportación e importación del tablero en JSON.
- Sincronización remota opcional con autenticación y resolución de conflictos.
