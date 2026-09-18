import { useEffect, useState } from 'react'

import fixture from '../../data/contact-form.json'
import { addField, moveField, removeField, updateField } from '../utils/operations'
import { formDefinitionSchema } from '../utils/schema'
import { createFormStorage } from '../utils/storage'
import type { FieldPatch } from '../utils/operations'
import type { FieldType, FormDefinition } from '../utils/types'

const initialForm = formDefinitionSchema.parse(fixture)

export interface FormBuilderState {
  form: FormDefinition
  error: string | null
  persistence: 'saved' | 'memory'
  add: (type: FieldType) => void
  update: (fieldId: string, patch: FieldPatch) => void
  move: (fieldId: string, direction: -1 | 1) => void
  remove: (fieldId: string) => void
  clearError: () => void
}

export const useFormBuilder = (): FormBuilderState => {
  const [form, setForm] = useState<FormDefinition>(initialForm)
  const [error, setError] = useState<string | null>(null)
  const [persistence, setPersistence] = useState<'saved' | 'memory'>('saved')

  useEffect(() => {
    try {
      const storedForm = createFormStorage().read()
      if (storedForm) setForm(storedForm)
    } catch {
      setPersistence('memory')
    }
  }, [])

  const apply = (operation: () => FormDefinition): void => {
    try {
      const nextForm = operation()
      setForm(nextForm)
      try {
        createFormStorage().write(nextForm)
        setPersistence('saved')
      } catch {
        setPersistence('memory')
      }
      setError(null)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'No se pudo actualizar el formulario')
    }
  }

  return {
    form,
    error,
    persistence,
    add: (type) => apply(() => addField(form, type, { id: `${type}-${crypto.randomUUID()}` })),
    update: (fieldId, patch) => apply(() => updateField(form, fieldId, patch)),
    move: (fieldId, direction) => apply(() => {
      const field = form.fields.find((candidate) => candidate.id === fieldId)
      if (!field) throw new Error(`Campo no encontrado: ${fieldId}`)
      return moveField(form, fieldId, field.position + direction)
    }),
    remove: (fieldId) => apply(() => removeField(form, fieldId)),
    clearError: () => setError(null),
  }
}