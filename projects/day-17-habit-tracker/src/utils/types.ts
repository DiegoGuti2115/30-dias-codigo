export type HabitFrequency = 'daily' | 'weekly';

export interface Habit {
  id: string;
  name: string;
  description?: string;
  frequency: HabitFrequency;
  createdAt: string; // ISO 8601
  color: string;
  isActive: boolean;
}

export interface HabitLog {
  habitId: string;
  date: string; // Formato YYYY-MM-DD para facilitar indexación
  completed: boolean;
}