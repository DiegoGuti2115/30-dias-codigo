# Roadmap — Temporizador Pomodoro

Este roadmap organiza el desarrollo del proyecto 16, una utilidad de Frontend construida con React y TypeScript. El objetivo es construir un temporizador atómico, funcional y presentable en menos de tres horas.

## Prioridades

- **P0 (Crítico):** Configurar el entorno React/TypeScript, implementar el motor del temporizador (lógica de cuenta atrás) y los controles básicos (start, pause, reset).
- **P1 (Importante):** Interfaz gráfica amigable, transiciones entre modos de trabajo/descanso y pruebas de renderizado. Preparar la demostración.
- **P2 (Opcional):** Notificaciones de audio o web, persistencia temporal (LocalStorage).

## Secuencia de Fases

```text
Fase 0 → Fase 1 → Fase 2 → Fase 3 → Fase 4 → Fase 5 → Fase 6

**FASE 0** — Preparación documental y estructural — Completada

Objetivo: Reservar la ubicación del proyecto en projects/day-16-pomodoro-timer y documentar el alcance.
Entregables: README.md, ROADMAP.md, carpetas src, tests, data, assets creadas.
Criterio de salida: El alcance está definido sin incluir características fuera del tiempo disponible (P0).

**FASE 1** — Diseño funcional y arquitectura de estado - Completada
Objetivo: Definir cómo React manejará el estado del tiempo y las transiciones.
Tareas: 
    Diseñar el esquema del estado global (tiempo restante, modo actual, estado de reproducción).
    Hacer un wireframe mental o boceto rápido de la UI.
Criterio de salida: Decisión tomada sobre qué hooks se usarán (ej. useState, useEffect, useRef).

**FASE 2** — Entorno de desarrollo React + TypeScript
Objetivo: Inicializar la aplicación base.
Tareas:
    Configurar el proyecto (usando Vite o la plantilla Next.js del repositorio).
    Limpiar el código base y configurar Tailwind CSS (opcional pero recomendado para rapidez).
Criterio de salida: Aplicación compilando correctamente en local (npm run dev) sin errores de tipado en un "Hola Mundo".

**FASE 3** — Implementación del núcleo (Hooks y Lógica)
Objetivo: Programar el comportamiento del temporizador independientemente del aspecto visual.
Tareas:
    Crear un hook personalizado (ej. usePomodoro) que gestione el setInterval y la limpieza (clearInterval).Implementar las funciones de formato de tiempo (de segundos a MM:SS).
Criterio de salida: La lógica de cuenta atrás funciona, se pausa y se reinicia correctamente a nivel de consola o estado.

**FASE 4** — Interfaz de usuario (UI) y Componentes
Objetivo: Construir la interfaz gráfica interactiva.
Tareas:
    Crear componentes: TimerDisplay, Controls (Botones), ModeSelector.
    Aplicar estilos visuales diferenciados para Trabajo y Descanso.
Criterio de salida: La aplicación es usable mediante clics en el navegador, los tiempos se actualizan en pantalla y los modos cambian adecuadamente.

**FASE 5** — Pruebas y verificación
Objetivo: Asegurar la calidad y estabilidad de la versión atómica.
Tareas:
    Escribir pruebas unitarias para las funciones de formato de tiempo o testing de componentes clave (React Testing Library).
    Comprobar que no hay fugas de memoria por intervalos no limpiados.
Criterio de salida: Todos los tests pasan y la UI responde sin glitches al cambiar rápidamente de estados.

**FASE 6** — Documentación, Demo y Publicación
Objetivo: Preparar el proyecto para su exhibición diaria en el catálogo y LinkedIn.
Tareas:
    Grabar la demostración de 15 segundos enfocada en la funcionalidad UI.
    Redactar el post diario explicando el reto técnico (ej. manejo de setInterval en React con useEffect).Asegurar que no existan secretos expuestos en el código[cite: 2].
Criterio de salida: El proyecto está documentado, commiteado, y la publicación lista para salir.

Ambos archivos sientan una base perfecta y estructurada para abordar las siguientes fases. Cuando estés listo para comenzar con el código de la aplicación React (Fase 2 y 3) y la lógica de *hooks*, dime y nos ponemos con ello.