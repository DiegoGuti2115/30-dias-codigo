import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';
import type { HabitFrequency } from '../utils/types';

type NewHabit = {
  name: string;
  description: string;
  frequency: HabitFrequency;
  color: string;
};

interface HabitFormProps {
  onSubmit: (habit: NewHabit) => void;
  onCancel: () => void;
}

const INITIAL_VALUES: NewHabit = {
  name: '',
  description: '',
  frequency: 'daily',
  color: '#2563eb',
};

export const HabitForm = ({ onSubmit, onCancel }: HabitFormProps) => {
  const [values, setValues] = useState<NewHabit>(INITIAL_VALUES);
  const [nameError, setNameError] = useState('');

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onCancel();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onCancel]);

  const updateValue = <Field extends keyof NewHabit>(field: Field, value: NewHabit[Field]) => {
    setValues((current) => ({ ...current, [field]: value }));
    if (field === 'name' && nameError) {
      setNameError('');
    }
  };

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const name = values.name.trim();

    if (!name) {
      setNameError('Escribe un nombre para el hábito.');
      return;
    }

    onSubmit({ ...values, name, description: values.description.trim() });
    setValues(INITIAL_VALUES);
  };

  return (
    <div className="fixed inset-0 z-10 flex items-center justify-center bg-gray-900/50 p-4" role="dialog" aria-modal="true" aria-labelledby="habit-form-title">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md space-y-5 rounded-xl bg-white p-6 shadow-xl"
        aria-labelledby="habit-form-title"
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 id="habit-form-title" className="text-xl font-bold text-gray-900">Nuevo hábito</h2>
            <p className="mt-1 text-sm text-gray-500">Define una práctica que quieras mantener.</p>
          </div>
          <button
            type="button"
            onClick={onCancel}
            className="text-2xl leading-none text-gray-400 hover:text-gray-700"
            aria-label="Cerrar formulario"
          >
            ×
          </button>
        </div>

        <div>
          <label htmlFor="habit-name" className="mb-1.5 block text-sm font-semibold text-gray-700">Nombre</label>
          <input
            id="habit-name"
            name="name"
            type="text"
            value={values.name}
            onChange={(event) => updateValue('name', event.target.value)}
            placeholder="Ej. Leer 20 minutos"
            aria-invalid={Boolean(nameError)}
            aria-describedby={nameError ? 'habit-name-error' : undefined}
            autoFocus
            className="w-full rounded-lg border border-gray-300 px-3 py-2.5 text-gray-900 outline-none transition focus:border-gray-900 focus:ring-2 focus:ring-gray-200"
          />
          {nameError && <p id="habit-name-error" className="mt-1.5 text-sm text-red-600">{nameError}</p>}
        </div>

        <div>
          <label htmlFor="habit-description" className="mb-1.5 block text-sm font-semibold text-gray-700">Descripción <span className="font-normal text-gray-400">(opcional)</span></label>
          <textarea
            id="habit-description"
            name="description"
            value={values.description}
            onChange={(event) => updateValue('description', event.target.value)}
            placeholder="Añade un poco de contexto"
            rows={3}
            className="w-full resize-none rounded-lg border border-gray-300 px-3 py-2.5 text-gray-900 outline-none transition focus:border-gray-900 focus:ring-2 focus:ring-gray-200"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="habit-frequency" className="mb-1.5 block text-sm font-semibold text-gray-700">Frecuencia</label>
            <select
              id="habit-frequency"
              name="frequency"
              value={values.frequency}
              onChange={(event) => updateValue('frequency', event.target.value as HabitFrequency)}
              className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-gray-900 outline-none focus:border-gray-900 focus:ring-2 focus:ring-gray-200"
            >
              <option value="daily">Diaria</option>
              <option value="weekly">Semanal</option>
            </select>
          </div>
          <div>
            <label htmlFor="habit-color" className="mb-1.5 block text-sm font-semibold text-gray-700">Color</label>
            <input
              id="habit-color"
              name="color"
              type="color"
              value={values.color}
              onChange={(event) => updateValue('color', event.target.value)}
              className="h-11 w-full cursor-pointer rounded-lg border border-gray-300 bg-white p-1"
            />
          </div>
        </div>

        <div className="flex justify-end gap-3 border-t border-gray-100 pt-4">
          <button type="button" onClick={onCancel} className="rounded-lg px-4 py-2.5 text-sm font-semibold text-gray-600 hover:bg-gray-100">Cancelar</button>
          <button type="submit" className="rounded-lg bg-gray-900 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-gray-800">Guardar hábito</button>
        </div>
      </form>
    </div>
  );
};
