import { openDB, type DBSchema } from 'idb';
import type { Habit, HabitLog } from '../utils/types';

interface HabitDatabase extends DBSchema {
  habits: {
    key: string;
    value: Habit;
  };
  logs: {
    key: string;
    value: HabitLog;
  };
}

export interface HabitSnapshot {
  habits: Habit[];
  logs: HabitLog[];
}

const DATABASE_NAME = 'habit-tracker';
const DATABASE_VERSION = 1;

const getDatabase = () => openDB<HabitDatabase>(DATABASE_NAME, DATABASE_VERSION, {
  upgrade(database) {
    if (!database.objectStoreNames.contains('habits')) {
      database.createObjectStore('habits');
    }
    if (!database.objectStoreNames.contains('logs')) {
      database.createObjectStore('logs');
    }
  },
});

export const loadHabitSnapshot = async (): Promise<HabitSnapshot> => {
  const database = await getDatabase();
  const [habits, logs] = await Promise.all([
    database.getAll('habits'),
    database.getAll('logs'),
  ]);
  database.close();
  return { habits, logs };
};

export const saveHabitSnapshot = async ({ habits, logs }: HabitSnapshot): Promise<void> => {
  const database = await getDatabase();
  const transaction = database.transaction(['habits', 'logs'], 'readwrite');

  await Promise.all([
    transaction.objectStore('habits').clear(),
    transaction.objectStore('logs').clear(),
  ]);

  await Promise.all([
    ...habits.map((habit) => transaction.objectStore('habits').put(habit, habit.id)),
    ...logs.map((log) => transaction.objectStore('logs').put(log, `${log.habitId}:${log.date}`)),
  ]);

  await transaction.done;
  database.close();
};
