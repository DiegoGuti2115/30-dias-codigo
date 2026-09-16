import type { Habit, HabitLog } from './types';

export const toggleHabitLog = (logs: HabitLog[], habitId: string, date: string): HabitLog[] => {
  const existingLogIndex = logs.findIndex(
    (log) => log.habitId === habitId && log.date === date,
  );

  if (existingLogIndex >= 0) {
    return logs.filter((_, index) => index !== existingLogIndex);
  }

  return [...logs, { habitId, date, completed: true }];
};

export const removeHabitAndLogs = (
  habits: Habit[],
  logs: HabitLog[],
  habitId: string,
): { habits: Habit[]; logs: HabitLog[] } => ({
  habits: habits.filter((habit) => habit.id !== habitId),
  logs: logs.filter((log) => log.habitId !== habitId),
});
