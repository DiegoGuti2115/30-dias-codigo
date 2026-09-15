# Día 16 — Temporizador Pomodoro

> Proyecto de la categoría Frontend del reto [30 Días, 30 Proyectos](../../README.md). **Estado:** Fases 0 a 6 completadas (v1 funcional).

## Propósito

El Temporizador Pomodoro es una aplicación frontend desarrollada en React y TypeScript diseñada para facilitar la gestión del tiempo mediante la técnica Pomodoro. Permite a los usuarios alternar entre bloques de trabajo concentrado y descansos cortos o largos, mejorando la productividad y el enfoque.

## Alcance cerrado de la versión 1

- Interfaz de usuario intuitiva construida con React.
- Temporizador preciso gestionado mediante *hooks* de estado.
- Modos predefinidos: Trabajo (25 min), Descanso Corto (5 min) y Descanso Largo (15 min).
- Controles básicos: Iniciar, Pausar y Reiniciar.
- Alerta visual y/o sonora básica al finalizar un ciclo.
- Diseño *responsive* adaptado a diferentes resoluciones.

## Fuera de alcance

- Autenticación de usuarios o creación de cuentas.
- Persistencia de historial de sesiones en bases de datos externas.
- Integración con APIs en la nube o sincronización entre dispositivos.
- Gestión de tareas complejas (To-Do list integrada).
- Personalización avanzada de tiempos por parte del usuario en esta v1.

## Requisitos y ejecución local

Dado que es un proyecto de frontend puro sin dependencias externas complejas, el entorno local requiere:

- Node.js `>=20.0.0` y npm `>=10.0.0`.

Desde el directorio del proyecto, instala las dependencias y lanza el entorno de desarrollo:

```bash
npm install
npm run dev

La aplicación estará disponible en http://localhost:3000 (o el puerto indicado por Vite/Next.js).

Estructura del proyecto
Cumpliendo con la organización del repositorio, el proyecto se estructura así:  

projects/day-16-pomodoro-timer/
├── README.md            # Instalación, uso y alcance del proyecto
├── ROADMAP.md           # Fases, prioridades y criterios de salida
├── package.json         # Manifiesto npm y dependencias de React/TypeScript
├── src/                 # Código ejecutable (Componentes y Hooks de React)
├── tests/               # Pruebas automatizadas de componentes y estado
├── data/                # Fixtures (configuración inicial de tiempos si aplica)
└── assets/              # Recursos gráficos y guion de demo para LinkedIn