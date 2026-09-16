import { useCallback, useEffect, useState } from 'react';
import type { Habit, HabitLog } from '../utils/types';
import { MOCK_HABITS, MOCK_LOGS } from '../db/mocks';
import { loadHabitSnapshot, saveHabitSnapshot } from '../db/storage';
import { toggleHabitLog as toggleHabitLogState } from '../utils/habitState';

export const useHabits = () => {
  const [habits, setHabits] = useState<Habit[]>([]);
  const [logs, setLogs] = useState<HabitLog[]>([]);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    let isCancelled = false;

    const hydrate = async () => {
      try {
        const snapshot = await loadHabitSnapshot();
        const isFirstRun = snapshot.habits.length === 0 && snapshot.logs.length === 0;

        if (!isCancelled) {
          setHabits(isFirstRun ? MOCK_HABITS : snapshot.habits);
          setLogs(isFirstRun ? MOCK_LOGS : snapshot.logs);
          setIsReady(true);
        }
      } catch {
        if (!isCancelled) {
          setHabits(MOCK_HABITS);
          setLogs(MOCK_LOGS);
          setIsReady(true);
        }
      }
    };

    void hydrate();

    return () => {
      isCancelled = true;
    };
  }, []);

  useEffect(() => {
    if (isReady) {
      void saveHabitSnapshot({ habits, logs });
    }
  }, [habits, logs, isReady]);

  // Función pura para obtener el status de un hábito en una fecha específica
  const getHabitStatus = useCallback((habitId: string, date: string): boolean => {
    return logs.some(log => log.habitId === habitId && log.date === date && log.completed);
  }, [logs]);

  // Toggle de un registro (completar/desmarcar)
  const toggleHabitLog = useCallback((habitId: string, date: string) => {
    setLogs((prevLogs) => toggleHabitLogState(prevLogs, habitId, date));
  }, []);

  const addHabit = useCallback((newHabit: Omit<Habit, 'id' | 'createdAt' | 'isActive'>) => {
    const habit: Habit = {
      ...newHabit,
      id: crypto.randomUUID(),
      createdAt: new Date().toISOString(),
      isActive: true,
    };
    setHabits(prev => [...prev, habit]);
  }, []);

  const deleteHabit = useCallback((habitId: string) => {
    setHabits((prevHabits) => prevHabits.filter((habit) => habit.id !== habitId));
    setLogs((prevLogs) => prevLogs.filter((log) => log.habitId !== habitId));
  }, []);

  return {
    habits: habits.filter(h => h.isActive),
    logs,
    getHabitStatus,
    toggleHabitLog,
    addHabit,
    deleteHabit,
    isReady,
  };
};