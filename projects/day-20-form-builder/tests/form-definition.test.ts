import { describe, expect, it } from 'vitest'

import fixture from '../data/contact-form.json'
import { cloneFormDefinition, normalizeFormDefinition } from '../src/utils/normalize'
import { addField, moveField, removeField, updateField } from '../src/utils/operations'
import { formDefinitionSchema } from '../src/utils/schema'
import { FIELD_TYPES, type FormDefinition } from '../src/utils/types'

const fixtureForm = formDefinitionSchema.parse(fixture)

describe('formDefinitionSchema', () => {
  it('valida el fixture de contacto', () => {
    const result = formDefinitionSchema.safeParse(fixture)

    expect(result.success).toBe(true)
  })

  it('rechaza nombres internos duplicados', () => {
    const invalidForm = {
      ...fixtureForm,
      fields: fixtureForm.fields.map((field, index) => index === 1
        ? { ...field, name: fixtureForm.fields[0].name }
        : field),
    }

    const result = formDefinitionSchema.safeParse(invalidForm)

    expect(result.success).toBe(false)
  })

  it('rechaza opciones duplicadas en un select', () => {
    const invalidForm = {
      ...fixtureForm,
      fields: fixtureForm.fields.map((field) => field.type === 'select'
        ? {
            ...field,
            options: [field.options[0], { ...field.options[1], value: field.options[0].value }],
          }
        : field),
    }

    const result = formDefinitionSchema.safeParse(invalidForm)

    expect(result.success).toBe(false)
  })
})

describe('normalizeFormDefinition', () => {
  it('normaliza texto, nombres y posiciones sin cambiar la forma del formulario', () => {
    const normalized = normalizeFormDefinition({
      ...fixtureForm,
      name: '  Contact Form  ',
      title: '  Contacto   rápido ',
      fields: fixtureForm.fields.map((field, index) => ({
        ...field,
        name: index === 0 ? ' Full Name ' : field.name,
        label: ` ${field.label} `,
        position: 99,
      })),
    })

    expect(normalized.name).toBe('contact_form')
    expect(normalized.title).toBe('Contacto rápido')
    expect(normalized.fields[0].name).toBe('full_name')
    expect(normalized.fields.map((field) => field.position)).toEqual([0, 1, 2, 3, 4])
  })

  it('clona las opciones para evitar mutaciones compartidas', () => {
    const clone = cloneFormDefinition(fixtureForm)
    const originalSelect = fixtureForm.fields.find((field) => field.type === 'select')
    const clonedSelect = clone.fields.find((field) => field.type === 'select')

    expect(clonedSelect).not.toBe(originalSelect)
    if (clonedSelect?.type === 'select' && originalSelect?.type === 'select') {
      expect(clonedSelect.options).not.toBe(originalSelect.options)
    }
  })
})

describe('form field operations', () => {
  it('builds a valid empty form with every supported field type', () => {
    const emptyForm = { ...fixtureForm, fields: [] }
    const result = FIELD_TYPES.reduce<FormDefinition>(
      (current, type, index) => addField(current, type, { id: `${type}-${index}` }),
      emptyForm,
    )

    expect(result.fields.map((field) => field.type)).toEqual([...FIELD_TYPES])
    expect(result.fields.map((field) => field.position)).toEqual([0, 1, 2, 3, 4, 5])
    expect(formDefinitionSchema.safeParse(result).success).toBe(true)
  })

  it('adds each field type with defaults and a unique name', () => {
    const withText = addField(fixtureForm, 'text', { id: 'phone-field', name: 'email' })
    const withSelect = addField(withText, 'select', { id: 'priority-field' })

    expect(withSelect.fields.at(-2)).toMatchObject({
      id: 'phone-field',
      type: 'text',
      name: 'email_2',
      label: 'Texto',
    })
    expect(withSelect.fields.at(-1)).toMatchObject({
      id: 'priority-field',
      type: 'select',
      name: 'select',
      options: [{ value: 'option_1' }],
    })
  })

  it('updates common and type-specific properties without mutating the source', () => {
    const updated = updateField(fixtureForm, 'full-name', {
      label: ' Nombre de la persona ',
      type: 'textarea',
      minLength: 5,
      maxLength: 120,
    })

    expect(updated.fields[0]).toMatchObject({
      type: 'textarea',
      label: 'Nombre de la persona',
      minLength: 5,
      maxLength: 120,
    })
    expect(fixtureForm.fields[0]).toMatchObject({ type: 'text', label: 'Nombre completo' })
  })

  it('moves fields to an explicit target position and reindexes them', () => {
    const moved = moveField(fixtureForm, 'message', 0)

    expect(moved.fields.map((field) => field.id)).toEqual([
      'message',
      'full-name',
      'email',
      'topic',
      'newsletter',
    ])
    expect(moved.fields.map((field) => field.position)).toEqual([0, 1, 2, 3, 4])
  })

  it('removes a field without mutating the source', () => {
    const reduced = removeField(fixtureForm, 'topic')

    expect(reduced.fields.map((field) => field.id)).not.toContain('topic')
    expect(reduced.fields.map((field) => field.position)).toEqual([0, 1, 2, 3])
    expect(fixtureForm.fields).toHaveLength(5)
  })

  it('rejects unknown fields and invalid target positions', () => {
    expect(() => updateField(fixtureForm, 'missing', { label: 'No existe' })).toThrow('Campo no encontrado')
    expect(() => moveField(fixtureForm, 'email', 10)).toThrow('Posición inválida')
    expect(() => removeField(fixtureForm, 'missing')).toThrow('Campo no encontrado')
  })
})