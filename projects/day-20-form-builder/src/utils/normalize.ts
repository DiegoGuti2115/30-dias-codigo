import type { FormDefinition, FormField } from './types'

const collapseWhitespace = (value: string): string => value.trim().replace(/\s+/g, ' ')

export const normalizeIdentifier = (value: string): string => collapseWhitespace(value)
  .toLowerCase()
  .replace(/[^a-z0-9]+/g, '_')
  .replace(/^_+|_+$/g, '')

const normalizeField = (field: FormField, position: number): FormField => {
  const common = {
    ...field,
    id: field.id.trim(),
    name: normalizeIdentifier(field.name),
    label: collapseWhitespace(field.label),
    helpText: collapseWhitespace(field.helpText),
    placeholder: collapseWhitespace(field.placeholder),
    position,
  }

  if (field.type !== 'select') {
    return { ...common, type: field.type }
  }

  return {
    ...common,
    type: 'select',
    options: field.options.map((option) => ({
      id: option.id.trim(),
      label: collapseWhitespace(option.label),
      value: collapseWhitespace(option.value),
    })),
  }
}

export const normalizeFormDefinition = (form: FormDefinition): FormDefinition => ({
  id: form.id.trim(),
  name: normalizeIdentifier(form.name),
  title: collapseWhitespace(form.title),
  description: collapseWhitespace(form.description),
  fields: form.fields.map(normalizeField),
})

export const cloneFormDefinition = (form: FormDefinition): FormDefinition => ({
  ...form,
  fields: form.fields.map((field) => ({
    ...field,
    ...(field.type === 'select'
      ? { options: field.options.map((option) => ({ ...option })) }
      : {}),
  })),
})