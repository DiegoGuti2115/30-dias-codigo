import { useState } from 'react'

import { validateFormResponse, type FormResponse, type ValidationErrors } from '../utils/responseValidation'
import type { FormField, FormDefinition } from '../utils/types'

interface PreviewFieldProps {
  field: FormField
  value: FormResponse[string]
  error?: string
  onChange: (value: FormResponse[string]) => void
}

const PreviewField = ({ field, value, error, onChange }: PreviewFieldProps) => {
  if (field.type === 'checkbox') {
    return <><label className="preview-check" htmlFor={`preview-${field.id}`}><input id={`preview-${field.id}`} type="checkbox" checked={value === true} onChange={(event) => onChange(event.target.checked)} /> <span>{field.label}{field.required && <b> *</b>}</span></label>{error && <span className="preview-error">{error}</span>}</>
  }

  if (field.type === 'select') {
    return <><select id={`preview-${field.id}`} value={typeof value === 'string' ? value : ''} onChange={(event) => onChange(event.target.value)} aria-invalid={Boolean(error)}><option value="" disabled>{field.placeholder || 'Selecciona una opción'}</option>{field.options.map((option) => <option key={option.id} value={option.value}>{option.label}</option>)}</select>{error && <span className="preview-error">{error}</span>}</>
  }

  if (field.type === 'textarea') return <><textarea id={`preview-${field.id}`} value={typeof value === 'string' ? value : ''} onChange={(event) => onChange(event.target.value)} placeholder={field.placeholder} rows={4} aria-invalid={Boolean(error)} />{error && <span className="preview-error">{error}</span>}</>
  return <><input id={`preview-${field.id}`} type={field.type} value={typeof value === 'string' || typeof value === 'number' ? value : ''} onChange={(event) => onChange(event.target.value)} placeholder={field.placeholder} aria-invalid={Boolean(error)} />{error && <span className="preview-error">{error}</span>}</>
}

export const FormPreview = ({ form }: { form: FormDefinition }) => {
  const [mode, setMode] = useState<'preview' | 'test'>('preview')
  const [response, setResponse] = useState<FormResponse>({})
  const [errors, setErrors] = useState<ValidationErrors>({})
  const [submitted, setSubmitted] = useState(false)

  const updateValue = (fieldName: string, value: FormResponse[string]) => {
    setResponse((current) => ({ ...current, [fieldName]: value }))
    setErrors((current) => {
      const next = { ...current }
      delete next[form.fields.find((field) => field.name === fieldName)?.id ?? '']
      return next
    })
    setSubmitted(false)
  }

  const submit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const result = validateFormResponse(form, response)
    setErrors(result.errors)
    setSubmitted(result.success)
  }

  return (
    <section className="preview-panel" aria-labelledby="preview-title">
      <div className="preview-panel__topline"><div className="preview-tabs" role="tablist" aria-label="Modo de formulario"><button type="button" role="tab" aria-selected={mode === 'preview'} className={mode === 'preview' ? 'is-active' : ''} onClick={() => setMode('preview')}>Vista previa</button><button type="button" role="tab" aria-selected={mode === 'test'} className={mode === 'test' ? 'is-active' : ''} onClick={() => setMode('test')}>Probar formulario</button></div><span className="live-dot">En directo</span></div>
      <div className="preview-paper">
        <div className="preview-mark">FB / 20</div>
        <h2 id="preview-title">{form.title}</h2>
        <p className="preview-description">{form.description}</p>
        {mode === 'preview' ? <div className="preview-note">Modo diseño <span>Activa “Probar formulario” para validar respuestas.</span></div> : (
          <form onSubmit={submit} noValidate>
            {form.fields.length === 0 && <div className="empty-state">Añade un campo desde el constructor para empezar la prueba.</div>}
            {form.fields.map((field) => (
              <div className="preview-field" key={field.id}>
                {field.type !== 'checkbox' && <label htmlFor={`preview-${field.id}`}>{field.label}{field.required && <b> *</b>}</label>}
                <PreviewField field={field} value={response[field.name]} error={errors[field.id]} onChange={(value) => updateValue(field.name, value)} />
                {field.helpText && <small>{field.helpText}</small>}
              </div>
            ))}
            {submitted && <div className="success-message" role="status">Formulario válido. Envío simulado correctamente.</div>}
            <button className="submit-preview" type="submit">Validar formulario <span>↗</span></button>
          </form>
        )}
      </div>
    </section>
  )
}