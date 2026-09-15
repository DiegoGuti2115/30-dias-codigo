# Fase 1: Diseño funcional y arquitectura de estado

Este documento registra las decisiones arquitectónicas y de diseño de interfaz para el proyecto **Temporizador Pomodoro** (Día 16), sirviendo como plano de construcción para las siguientes fases de desarrollo.

## 1. Arquitectura del Estado Global

Para mantener el componente principal limpio y modular, toda la lógica de estado se encapsulará en un *hook* personalizado (`usePomodoro`). El estado del temporizador se basará en tres piezas fundamentales:

*   **`mode` (Modo actual):** Un `string` o `enum` que indicará en qué ciclo nos encontramos (`work`, `shortBreak`, `longBreak`).
*   **`timeLeft` (Tiempo restante):** El tiempo restante almacenado estrictamente en segundos (número entero). Se iniciará por defecto en 1500 segundos (25 minutos) para el modo de trabajo clásico. Sin embargo, la lógica se diseñará de forma escalable y flexible para permitir, en el futuro, bloques de estudio focalizado de 90 minutos u otras duraciones personalizadas.
*   **`isRunning` (Estado de ejecución):** Un valor booleano (`true`/`false`) que determinará si la cuenta atrás del temporizador está activa o se encuentra en pausa.

## 2. Boceto de la Interfaz (Wireframe)

La interfaz de usuario será minimalista para evitar distracciones y maximizar el enfoque. Visualmente, se dividirá en tres áreas clave dispuestas de arriba a abajo:

1.  **Selector de Modos (Cabecera):** Tres botones tipo "pestaña" o "píldora" en la parte superior para alternar manualmente entre "Trabajo", "Descanso Corto" y "Descanso Largo".
2.  **Display Central (Cuerpo):** Un texto tipográfico de gran tamaño que mostrará el tiempo restante en formato `MM:SS`. Para mejorar el *feedback* visual y la experiencia de usuario (UX), el color de fondo de toda la aplicación cambiará de forma suave y animada dependiendo del modo activo (por ejemplo, rojo/naranja para trabajo, azul/verde para descanso).
3.  **Controles Base (Pie):** 
    *   Un botón principal y prominente para "Iniciar / Pausar" que alternará su texto/icono según el estado de `isRunning`.
    *   Un botón secundario y discreto para "Reiniciar" el tiempo del ciclo actual a su valor por defecto.

## 3. Decisión de Hooks (Criterio de Salida)

Para gestionar eficientemente el estado reactivo y los ciclos de vida de la cuenta atrás en React, se utilizará la siguiente combinación de *hooks* nativos:

*   **`useState`:** Gestionará las tres variables reactivas del estado global mencionadas anteriormente (`mode`, `timeLeft`, `isRunning`), garantizando que la interfaz se actualice (re-renderice) cada vez que el tiempo cambie o se pause la aplicación.
*   **`useEffect`:** Será el corazón o motor del temporizador. Este *hook* reaccionará a los cambios de `isRunning`. Cuando sea `true`, instanciará un `setInterval` que restará un segundo a `timeLeft` de forma recurrente. Fundamentalmente, se aprovechará la función de limpieza (el `return` del *hook*) para ejecutar `clearInterval`, evitando fugas de memoria (*memory leaks*) o solapamientos de intervalos.
*   **`useRef`:** Se empleará para almacenar la referencia estricta y mutable del identificador del intervalo (`intervalId`). Al contrario que `useState`, las mutaciones en `useRef` no disparan renderizados, lo que lo convierte en la herramienta perfecta para mantener el control técnico sobre el reloj en segundo plano sin penalizar el rendimiento.