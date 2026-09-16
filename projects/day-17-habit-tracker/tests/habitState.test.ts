import { describe, expect, it } from 'vitest';
import { removeHabitAndLogs, toggleHabitLog } from '../src/utils/habitState';
import type { Habit, HabitLog } from '../src/utils/types';

const habit: Habit = {
  id: 'habit-1',
  name: 'Caminar',
  description: 'Paseo diario',
  frequency: 'daily',
  createdAt: '2026-09-16T08:00:00.000Z',
  color: '#2563eb',
  isActive: true,
};

const existingLogs: HabitLog[] = [
  { habitId: habit.id, date: '2026-09-10', completed: true },
  { habitId: 'habit-2', date: '2026-09-10', completed: true },
];

describe('habit state operations', () => {
  it('marks a past date and removes it on the next toggle', () => {
    const markedLogs = toggleHabitLog([], habit.id, '2026-09-01');

    expect(markedLogs).toEqual([
      { habitId: habit.id, date: '2026-09-01', completed: true },
    ]);
    expect(toggleHabitLog(markedLogs, habit.id, '2026-09-01')).toEqual([]);
  });

  it('removes a habit and all of its history without affecting other habits', () => {
    const result = removeHabitAndLogs(
      [habit, { ...habit, id: 'habit-2', name: 'Leer' }],
      existingLogs,
      habit.id,
    );

    expect(result.habits.map((item) => item.id)).toEqual(['habit-2']);
    expect(result.logs).toEqual([
      { habitId: 'habit-2', date: '2026-09-10', completed: true },
    ]);
  });
});
