import { describe, expect, it } from 'vitest'

import fixture from '../data/contact-form.json'
import { addField } from '../src/utils/operations'
import { formDefinitionSchema } from '../src/utils/schema'
import { validateFormResponse } from '../src/utils/responseValidation'

const form = formDefinitionSchema.parse(fixture)

describe('validateFormResponse', () => {
  it('accepts a complete response and converts numeric values', () => {
    const result = validateFormResponse(form, {
      full_name: 'Ana García',
      email: 'ana@example.com',
      topic: 'support',
      message: 'Necesito ayuda con mi cuenta.',
      newsletter: true,
    })

    expect(result.success).toBe(true)
    expect(result.errors).toEqual({})
  })

  it('reports required fields by field id without dropping entered values', () => {
    const result = validateFormResponse(form, { full_name: '', email: 'bad' })

    expect(result.success).toBe(false)
    expect(result.errors['full-name']).toBe('Este campo es obligatorio.')
    expect(result.errors.email).toBe('Introduce un correo electrónico válido.')
    expect(result.values.email).toBe('bad')
  })

  it('rejects invalid selections and short text', () => {
    const result = validateFormResponse(form, {
      full_name: 'A',
      email: 'ana@example.com',
      topic: 'unknown',
      message: 'corto',
    })

    expect(result.errors['full-name']).toContain('al menos 2')
    expect(result.errors.topic).toBe('Selecciona una opción válida.')
    expect(result.errors.message).toContain('al menos 10')
  })

  it('requires a checked checkbox when configured as required', () => {
    const requiredForm = formDefinitionSchema.parse({
      ...form,
      fields: form.fields.map((field) => field.type === 'checkbox' ? { ...field, required: true } : field),
    })

    const result = validateFormResponse(requiredForm, {})

    expect(result.errors.newsletter).toBe('Debes aceptar esta opción.')
  })

  it('validates numeric boundaries and preserves the normalized number', () => {
    const numericForm = addField(form, 'number', { id: 'age', min: 18, max: 99 })
    const result = validateFormResponse(numericForm, { number: '17' })

    expect(result.errors.age).toBe('El valor mínimo es 18.')
    expect(result.values.number).toBe(17)
  })
})