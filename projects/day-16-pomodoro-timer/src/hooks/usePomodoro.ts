// src/hooks/usePomodoro.ts
import { useState, useEffect, useCallback } from 'react';
import { formatTime } from '../utils/timeFormatter';

export type Mode = 'work' | 'shortBreak' | 'longBreak';

// ¡Aquí está la constante exportada! Al añadir "export", permitimos que
// App.tsx lea estos totales para calcular el porcentaje del círculo SVG.
export const MODES_IN_SECONDS: Record<Mode, number> = {
  work: 90 * 60,       // 90 minutos de foco absoluto
  shortBreak: 5 * 60,  // Descanso rápido (ej. estirar)
  longBreak: 15 * 60,  // Descanso largo
};

export function usePomodoro() {
  const [mode, setMode] = useState<Mode>('work');
  const [timeLeft, setTimeLeft] = useState(MODES_IN_SECONDS.work);
  const [isRunning, setIsRunning] = useState(false);

  // El corazón del temporizador gestionado por el ciclo de vida de React
  useEffect(() => {
    let intervalId: number | undefined;

    if (isRunning && timeLeft > 0) {
      intervalId = window.setInterval(() => {
        setTimeLeft((prev) => prev - 1);
      }, 1000);
    } else if (timeLeft === 0) {
      setIsRunning(false);
    }

    // Función de limpieza: evita fugas de memoria al desmontar
    return () => {
      if (intervalId) window.clearInterval(intervalId);
    };
  }, [isRunning, timeLeft]);

  // Controles del reloj
  const toggleTimer = () => setIsRunning(!isRunning);

  const resetTimer = useCallback(() => {
    setIsRunning(false);
    setTimeLeft(MODES_IN_SECONDS[mode]);
  }, [mode]);

  const changeMode = (newMode: Mode) => {
    setMode(newMode);
    setIsRunning(false);
    setTimeLeft(MODES_IN_SECONDS[newMode]);
  };

  // Usamos la función pura que extrajimos para los tests en la Fase 5
  const formattedTime = formatTime(timeLeft);

  return {
    mode,
    timeLeft,
    isRunning,
    formattedTime,
    toggleTimer,
    resetTimer,
    changeMode,
  };
}