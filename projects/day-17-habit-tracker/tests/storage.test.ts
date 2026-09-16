import 'fake-indexeddb/auto';
import { deleteDB } from 'idb';
import { afterEach, describe, expect, it } from 'vitest';
import { loadHabitSnapshot, saveHabitSnapshot } from '../src/db/storage';
import type { Habit, HabitLog } from '../src/utils/types';

const DATABASE_NAME = 'habit-tracker';

const habit: Habit = {
  id: 'habit-persisted',
  name: 'Leer',
  frequency: 'daily',
  createdAt: '2026-09-16T08:00:00.000Z',
  color: '#10b981',
  isActive: true,
};

const log: HabitLog = {
  habitId: habit.id,
  date: '2026-09-15',
  completed: true,
};

afterEach(async () => {
  await deleteDB(DATABASE_NAME);
});

describe('habit IndexedDB storage', () => {
  it('loads habits and logs saved by a previous session', async () => {
    await saveHabitSnapshot({ habits: [habit], logs: [log] });

    await expect(loadHabitSnapshot()).resolves.toEqual({
      habits: [habit],
      logs: [log],
    });
  });

  it('replaces a deleted habit and its history in the persisted snapshot', async () => {
    await saveHabitSnapshot({ habits: [habit], logs: [log] });
    await saveHabitSnapshot({ habits: [], logs: [] });

    await expect(loadHabitSnapshot()).resolves.toEqual({ habits: [], logs: [] });
  });
});
