import { useState } from 'react';
import { useHabits } from '../hooks/useHabits';
import { HabitForm } from './HabitForm';
import { WeeklyGrid } from './WeeklyGrid';

export const HabitList = () => {
  const { habits, getHabitStatus, toggleHabitLog, addHabit, deleteHabit, isReady } = useHabits();
  
  const [isAdding, setIsAdding] = useState(false);

  if (!isReady) {
    return <div className="p-8 text-center text-sm font-medium text-gray-500">Cargando hábitos...</div>;
  }

  return (
    <div className="max-w-4xl mx-auto p-4 sm:p-6 space-y-8">
      {/* Header Orquestador */}
      <header className="flex justify-between items-end pb-4 border-b border-gray-200">
        <div>
          <h2 className="text-3xl font-extrabold text-gray-900 tracking-tight">Rastreador de Hábitos</h2>
          <p className="text-sm text-gray-500 mt-1 font-medium">Día 17 del Reto 30 Días</p>
        </div>
        <button 
          onClick={() => setIsAdding(true)}
          className="bg-gray-900 hover:bg-gray-800 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-900"
        >
          + Nuevo Hábito
        </button>
      </header>

      {/* Pipeline Visual de Hábitos */}
      <div className="space-y-4">
        {habits.length === 0 ? (
          <div className="text-center bg-gray-50 rounded-xl p-12 border-2 border-dashed border-gray-200">
            <p className="text-gray-500 font-medium">No hay hábitos activos en este entorno.</p>
          </div>
        ) : (
          habits.map((habit) => (
            <article 
              key={habit.id} 
              className="bg-white p-5 rounded-xl shadow-sm border border-gray-200 flex flex-col sm:flex-row sm:items-center justify-between gap-6 transition-all hover:shadow-md"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-3">
                  <h3 className="text-lg font-bold text-gray-900 flex items-center gap-3 truncate">
                    <span
                      className="w-3.5 h-3.5 rounded-full shadow-sm shrink-0"
                      style={{ backgroundColor: habit.color }}
                      aria-hidden="true"
                    />
                    {habit.name}
                  </h3>
                  <button
                    type="button"
                    onClick={() => deleteHabit(habit.id)}
                    className="shrink-0 text-sm font-semibold text-red-600 hover:text-red-800"
                    aria-label={`Eliminar hábito ${habit.name}`}
                  >
                    Eliminar
                  </button>
                </div>
                {habit.description && (
                  <p className="text-sm text-gray-500 mt-1.5 truncate">{habit.description}</p>
                )}
              </div>
              
              {/* Nodo Aislado: Grid de Rachas */}
              <div className="shrink-0 bg-gray-50 p-2 rounded-lg border border-gray-100">
                <WeeklyGrid 
                  habitId={habit.id}
                  habitColor={habit.color}
                  getHabitStatus={getHabitStatus}
                  toggleHabitLog={toggleHabitLog}
                />
              </div>
            </article>
          ))
        )}
      </div>

      {isAdding && (
        <HabitForm
          onSubmit={(habit) => {
            addHabit(habit);
            setIsAdding(false);
          }}
          onCancel={() => setIsAdding(false)}
        />
      )}
    </div>
  );
};