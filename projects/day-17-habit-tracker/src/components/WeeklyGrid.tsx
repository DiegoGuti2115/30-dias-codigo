import { useMemo } from 'react';

interface WeeklyGridProps {
  habitId: string;
  habitColor: string;
  getHabitStatus: (habitId: string, date: string) => boolean;
  toggleHabitLog: (habitId: string, date: string) => void;
}

export const WeeklyGrid = ({ habitId, habitColor, getHabitStatus, toggleHabitLog }: WeeklyGridProps) => {
  // Memoizamos las fechas para evitar recálculos en cada render de la UI
  const last7Days = useMemo(() => {
    return Array.from({ length: 7 }).map((_, i) => {
      const d = new Date();
      d.setDate(d.getDate() - (6 - i));
      return d.toISOString().split('T')[0];
    });
  }, []);

  return (
    <div className="flex gap-2">
      {last7Days.map((date) => {
        const isCompleted = getHabitStatus(habitId, date);
        
        return (
          <button
            key={date}
            onClick={() => toggleHabitLog(habitId, date)}
            className={`w-10 h-10 rounded-md transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-1`}
            style={{ 
              backgroundColor: isCompleted ? habitColor : '#f3f4f6',
              boxShadow: isCompleted ? `0 0 8px ${habitColor}40` : 'none'
            }}
            aria-label={`Marcar hábito para la fecha ${date}`}
            aria-pressed={isCompleted}
          />
        );
      })}
    </div>
  );
};