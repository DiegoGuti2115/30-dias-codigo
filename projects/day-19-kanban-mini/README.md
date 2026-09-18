# Kanban Mínimo

Aplicación web del Día 19 del reto [30 Días, 30 Proyectos](../../README.md). El objetivo es construir un tablero Kanban pequeño, claro y utilizable para organizar tareas en un flujo visual de trabajo.

**Estado:** v1 funcional, validada y lista para demostración local.

## Problema

Una lista plana de tareas no muestra con claridad qué está pendiente, qué está en progreso y qué ya se completó. Este proyecto concentra esas decisiones en un tablero con columnas y tarjetas que se pueden mover entre estados.

## Objetivo del MVP

Permitir que una persona gestione un tablero personal desde el navegador, sin backend ni cuentas, manteniendo una interacción rápida y una estructura de datos sencilla que pueda probarse de forma aislada.

## Alcance

- Mostrar un tablero con las columnas `Por hacer`, `En progreso` y `Completado`.
- Crear tarjetas con título obligatorio y descripción opcional.
- Editar el contenido de una tarjeta existente.
- Mover tarjetas entre columnas mediante controles accesibles; el arrastre visual queda como mejora opcional.
- Eliminar tarjetas con una acción explícita.
- Mostrar el número de tarjetas de cada columna.
- Conservar un orden estable dentro de cada columna.
- Mostrar estados vacíos cuando una columna no tenga tarjetas.
- Adaptar el tablero a escritorio y móvil.
- Mantener la lógica de columnas y tarjetas separada de los componentes visuales.
- Cubrir las operaciones principales con pruebas automatizadas.

## Fuera de alcance

- Autenticación, cuentas de usuario o permisos.
- Colaboración en tiempo real y múltiples tableros.
- Backend, API o base de datos remota.
- Sincronización entre dispositivos.
- Adjuntos, comentarios, notificaciones o fechas límite.
- Etiquetas, filtros avanzados y búsqueda global.
- Drag and drop avanzado con librerías externas en la primera versión.
- Historial de cambios, deshacer o auditoría.

## Tecnologías previstas

- React 19.
- TypeScript.
- Vite.
- CSS propio con variables de diseño y breakpoints responsive.
- Vitest para pruebas.
- IndexedDB mediante `idb` como persistencia local opcional del MVP, siguiendo el patrón offline-first de los proyectos anteriores.

## Requisitos

- Node.js 20 o superior.
- npm.
- Navegador moderno con soporte para IndexedDB.

## Instalación y comandos

La aplicación Vite/React y la base de pruebas están preparadas para desarrollo local:

```bash
npm install
npm run dev
npm run build
npm run lint
npm test
npm run preview
```

## Flujo principal

1. La aplicación carga un tablero inicial con tarjetas de ejemplo.
2. La persona usuaria crea una tarjeta desde el control de la columna correspondiente.
3. La tarjeta aparece en `Por hacer` y puede editarse.
4. La persona usuaria la mueve a `En progreso` y después a `Completado`.
5. Las acciones de edición, movimiento y eliminación actualizan el tablero sin recargar la página.
6. Cuando IndexedDB está disponible, una recarga conserva el tablero local y la cabecera indica `Guardado en este navegador`.
7. Si IndexedDB no está disponible o falla, la sesión continúa funcionando en memoria y aparece un aviso no bloqueante.

## Reglas del modelo

- Cada tarjeta tiene un identificador estable, título, descripción opcional, columna y posición.
- El título es obligatorio después de eliminar espacios exteriores.
- La descripción puede estar vacía.
- Una tarjeta pertenece siempre a una única columna válida.
- Las posiciones se recalculan al mover o eliminar para evitar huecos innecesarios.
- El orden de las tarjetas se conserva dentro de cada columna.
- Las fechas, si se incluyen para ordenar o mostrar actividad, se guardarán como cadenas ISO 8601 en UTC.
- Las columnas del MVP son fijas; crear columnas personalizadas queda fuera de alcance.

## Integración y fallback local

- **Ruta principal:** estado React en memoria durante la interacción y snapshot persistido en IndexedDB mediante `src/db/storage.ts`.
- **Fallback:** datos iniciales en `data/` y estado en memoria si IndexedDB no existe o una operación de lectura/escritura falla.
- **Criterio de cambio:** si la persistencia local no funciona antes de T+30, se conserva la experiencia en memoria y se continúa con la demo.
- No se requieren credenciales ni `.env.example` para el MVP.

## Decisiones técnicas

- La lógica de creación, edición, movimiento, eliminación y normalización vivirá en funciones puras para poder probarla sin montar React.
- El estado del tablero se expondrá mediante un hook, manteniendo los componentes enfocados en presentación y eventos.
- Las acciones de mover tarjeta tendrán controles visibles y accesibles; el drag and drop podrá añadirse después sin convertirlo en requisito del flujo principal.
- El adaptador de almacenamiento quedará detrás de una interfaz local para que IndexedDB no se filtre a toda la UI.
- El diseño priorizará lectura rápida del tablero, estados vacíos claros y buen comportamiento en pantallas pequeñas.

## Estructura prevista

```text
day-19-kanban-mini/
├── README.md                 # Alcance, instalación, decisiones y fallback
├── ROADMAP.md                # Fases, tareas y criterios de salida
├── package.json              # Scripts de validación del modelo
├── package-lock.json         # Versiones reproducibles de dependencias
├── tsconfig.json             # Configuración de TypeScript
├── vitest.config.ts          # Configuración de pruebas
├── eslint.config.js          # Reglas de lint del proyecto
├── index.html                # Entrada HTML de Vite
├── vite.config.ts            # Configuración del bundler y React
├── src/
│   ├── App.tsx               # Composición de la pantalla y modales
│   ├── components/           # Tablero, columnas, tarjetas y formularios
│   ├── db/                   # Adaptador IndexedDB y carga de datos iniciales
│   │   └── storage.ts        # API de lectura y escritura del snapshot
│   ├── hooks/                # Estado y operaciones del tablero
│   ├── index.css             # Sistema visual y responsive
│   ├── main.tsx              # Punto de montaje React
│   └── utils/                # Tipos, reglas y operaciones puras de Kanban
├── tests/                    # Pruebas de reglas, estado y persistencia
├── data/                     # Fixture inicial del tablero y tarjetas de demo
│   └── board.json            # Tablero de ejemplo distribuido en las tres columnas
├── assets/                   # Capturas, GIF o recursos de demostración
│   ├── README.md             # Criterios y estado de los assets
│   └── kanban-reference.png  # Captura visual del tablero validado
└── docs/                     # Guion de demo y borrador de publicación
	├── DEMO_SCRIPT.md        # Secuencia reproducible de 15 segundos
	└── LINKEDIN_POST.md      # Borrador de publicación
```

## Validación prevista

- Ejecutar la suite con `npm test`.
- Comprobar creación, edición, movimiento y eliminación de tarjetas.
- Verificar que una tarjeta no desaparece al cambiar de columna.
- Verificar persistencia tras recargar cuando IndexedDB está disponible.
- Verificar el fallback en memoria cuando IndexedDB falla.
- Revisar teclado, foco, nombres accesibles y responsive en escritorio y móvil.
- Ejecutar `npm run lint` y `npm run build` antes de cerrar el proyecto.

La validación actual incluye reglas de dominio, estado React, persistencia IndexedDB, fallback en memoria y revisión manual de foco, teclado y responsive.

## Demo

La demostración muestra en un máximo de 15 segundos la creación de una tarjeta, su paso por las tres columnas y su recuperación tras recargar. El guion reproducible está en [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md), el borrador de publicación en [`docs/LINKEDIN_POST.md`](docs/LINKEDIN_POST.md) y la captura visual validada en [`assets/kanban-reference.png`](assets/kanban-reference.png).
