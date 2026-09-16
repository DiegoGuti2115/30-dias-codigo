import type { Habit, HabitLog } from '../utils/types';

const today = new Date();
const formatDate = (date: Date) => date.toISOString().split('T')[0];

const getPastDate = (daysAgo: number) => {
  const d = new Date(today);
  d.setDate(d.getDate() - daysAgo);
  return formatDate(d);
};

export const MOCK_HABITS: Habit[] = [
  {
    id: 'h-1',
    name: 'Sesión de Calistenia',
    description: 'Dominadas, fondos, remos y flexiones en el parque.',
    frequency: 'daily',
    createdAt: getPastDate(10),
    color: '#3b82f6', // blue-500
    isActive: true,
  },
  {
    id: 'h-2',
    name: 'Sprints',
    description: 'Series de alta intensidad en pista de atletismo.',
    frequency: 'weekly',
    createdAt: getPastDate(10),
    color: '#ef4444', // red-500
    isActive: true,
  },
  {
    id: 'h-3',
    name: 'Bloque de Estudio Profundo',
    description: '90 minutos ininterrumpidos. Termodinámica o Regulación Automática.',
    frequency: 'daily',
    createdAt: getPastDate(10),
    color: '#8b5cf6', // violet-500
    isActive: true,
  },
  {
    id: 'h-4',
    name: 'Commit Reto 30 Días',
    description: 'Subir el proyecto diario del reto de desarrollo.',
    frequency: 'daily',
    createdAt: getPastDate(10),
    color: '#10b981', // emerald-500
    isActive: true,
  },
];

// Generar un historial mock para los últimos 5 días simulando consistencia
export const MOCK_LOGS: HabitLog[] = MOCK_HABITS.flatMap((habit) => {
  const logs: HabitLog[] = [];
  // Simulamos que los sprints son menos frecuentes
  const daysToLog = habit.id === 'h-2' ? [1, 4] : [0, 1, 2, 3, 4]; 
  
  daysToLog.forEach(daysAgo => {
    logs.push({
      habitId: habit.id,
      date: getPastDate(daysAgo),
      completed: true
    });
  });
  
  return logs;
});