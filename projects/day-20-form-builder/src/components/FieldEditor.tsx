import type { ChangeEvent } from 'react'

import type { FieldPatch } from '../utils/operations'
import type { FieldType, FormField } from '../utils/types'

interface FieldEditorProps {
  field: FormField
  index: number
  total: number
  onUpdate: (patch: FieldPatch) => void
  onMove: (direction: -1 | 1) => void
  onRemove: () => void
}

const typeLabels: Record<FieldType, string> = {
  text: 'Texto corto',
  email: 'Correo',
  number: 'Número',
  textarea: 'Texto largo',
  select: 'Selección',
  checkbox: 'Casilla',
}

const readNumber = (event: ChangeEvent<HTMLInputElement>): number | undefined => (
  event.target.value === '' ? undefined : Number(event.target.value)
)

export const FieldEditor = ({ field, index, total, onUpdate, onMove, onRemove }: FieldEditorProps) => {
  const update = (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    onUpdate({ [event.target.name]: event.target.value })
  }

  return (
    <article className="field-editor">
      <div className="field-editor__header">
        <div>
          <span className="field-number">{String(index + 1).padStart(2, '0')}</span>
          <span className="field-type">{typeLabels[field.type]}</span>
        </div>
        <div className="field-actions">
          <button type="button" className="icon-button" onClick={() => onMove(-1)} disabled={index === 0} aria-label={`Mover ${field.label} arriba`} title="Mover arriba">↑</button>
          <button type="button" className="icon-button" onClick={() => onMove(1)} disabled={index === total - 1} aria-label={`Mover ${field.label} abajo`} title="Mover abajo">↓</button>
          <button type="button" className="icon-button icon-button--danger" onClick={onRemove} aria-label={`Eliminar ${field.label}`} title="Eliminar campo">×</button>
        </div>
      </div>

      <div className="field-grid">
        <label>
          Etiqueta
          <input name="label" value={field.label} onChange={update} />
        </label>
        <label>
          Tipo
          <select name="type" value={field.type} onChange={update}>
            {(Object.keys(typeLabels) as FieldType[]).map((type) => <option key={type} value={type}>{typeLabels[type]}</option>)}
          </select>
        </label>
        <label>
          Nombre interno
          <input name="name" value={field.name} onChange={update} spellCheck="false" />
          <small>Se normaliza como identificador único.</small>
        </label>
        <label>
          Texto de ayuda
          <input name="helpText" value={field.helpText} onChange={update} />
        </label>
        {field.type !== 'checkbox' && (
          <label>
            Placeholder
            <input name="placeholder" value={field.placeholder} onChange={update} />
          </label>
        )}
        <label className="check-control">
          <input name="required" type="checkbox" checked={field.required} onChange={(event) => onUpdate({ required: event.target.checked })} />
          Campo obligatorio
        </label>
        {(field.type === 'text' || field.type === 'email' || field.type === 'textarea') && (
          <>
            <label>
              Mínimo de caracteres
              <input type="number" min="0" value={field.minLength ?? ''} onChange={(event) => onUpdate({ minLength: readNumber(event) })} />
            </label>
            <label>
              Máximo de caracteres
              <input type="number" min="0" value={field.maxLength ?? ''} onChange={(event) => onUpdate({ maxLength: readNumber(event) })} />
            </label>
          </>
        )}
        {field.type === 'number' && (
          <>
            <label>
              Valor mínimo
              <input type="number" value={field.min ?? ''} onChange={(event) => onUpdate({ min: readNumber(event) })} />
            </label>
            <label>
              Valor máximo
              <input type="number" value={field.max ?? ''} onChange={(event) => onUpdate({ max: readNumber(event) })} />
            </label>
          </>
        )}
      </div>

      {field.type === 'select' && (
        <div className="options-editor">
          <div className="section-label">Opciones</div>
          {field.options.map((option, optionIndex) => (
            <div className="option-row" key={option.id}>
              <input aria-label={`Etiqueta de opción ${optionIndex + 1}`} value={option.label} onChange={(event) => onUpdate({ options: field.options.map((candidate) => candidate.id === option.id ? { ...candidate, label: event.target.value } : candidate) })} />
              <input aria-label={`Valor de opción ${optionIndex + 1}`} value={option.value} onChange={(event) => onUpdate({ options: field.options.map((candidate) => candidate.id === option.id ? { ...candidate, value: event.target.value } : candidate) })} />
            </div>
          ))}
          <button type="button" className="text-button" onClick={() => onUpdate({ options: [...field.options, { id: `option-${crypto.randomUUID()}`, label: `Opción ${field.options.length + 1}`, value: `option_${field.options.length + 1}` }] })}>+ Añadir opción</button>
        </div>
      )}
    </article>
  )
}