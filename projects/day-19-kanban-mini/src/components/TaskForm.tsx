import { useEffect, useState, type FormEvent } from 'react'
import type { CardDraft } from '../utils/types'

interface TaskFormProps {
  initialDraft?: CardDraft
  isEditing: boolean
  onSubmit: (draft: CardDraft) => void
  onCancel: () => void
}

export function TaskForm({ initialDraft, isEditing, onSubmit, onCancel }: TaskFormProps) {
  const [title, setTitle] = useState(initialDraft?.title ?? '')
  const [description, setDescription] = useState(initialDraft?.description ?? '')

  useEffect(() => {
    setTitle(initialDraft?.title ?? '')
    setDescription(initialDraft?.description ?? '')
  }, [initialDraft])

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    onSubmit({ title, description })
  }

  return (
    <form className="task-form" onSubmit={handleSubmit}>
      <div className="form-heading">
        <div>
          <span className="eyebrow">{isEditing ? 'Editar tarjeta' : 'Nueva tarjeta'}</span>
          <h2 id="form-title">{isEditing ? 'Ajusta los detalles' : 'Pon una tarea en marcha'}</h2>
        </div>
        <button className="icon-button" type="button" onClick={onCancel} aria-label="Cerrar formulario">
          <span aria-hidden="true">×</span>
        </button>
      </div>
      <label>
        Título
        <input
          autoFocus
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          placeholder="Ej. Preparar la demo"
          maxLength={100}
          required
        />
      </label>
      <label>
        Descripción <span className="optional">Opcional</span>
        <textarea
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          placeholder="¿Qué significa terminarla?"
          rows={4}
          maxLength={280}
        />
      </label>
      <div className="form-actions">
        <button className="button button-quiet" type="button" onClick={onCancel}>Cancelar</button>
        <button className="button button-primary" type="submit">{isEditing ? 'Guardar cambios' : 'Añadir tarjeta'}</button>
      </div>
    </form>
  )
}
