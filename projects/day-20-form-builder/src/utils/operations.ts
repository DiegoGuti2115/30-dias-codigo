import { formDefinitionSchema } from './schema'
import { cloneFormDefinition, normalizeFormDefinition, normalizeIdentifier } from './normalize'
import type { FieldOption, FieldType, FormDefinition, FormField } from './types'

export interface AddFieldOptions {
  id: string
  name?: string
  label?: string
  helpText?: string
  placeholder?: string
  required?: boolean
  minLength?: number
  maxLength?: number
  min?: number
  max?: number
  options?: FieldOption[]
}

export interface FieldPatch {
  type?: FieldType
  name?: string
  label?: string
  helpText?: string
  placeholder?: string
  required?: boolean
  minLength?: number
  maxLength?: number
  min?: number
  max?: number
  options?: FieldOption[]
}

const defaultLabel = (type: FieldType): string => {
  if (type === 'textarea') return 'Descripción'
  if (type === 'checkbox') return 'Acepto las condiciones'
  if (type === 'select') return 'Selección'
  if (type === 'email') return 'Correo electrónico'
  if (type === 'number') return 'Número'
  return 'Texto'
}

const defaultOptions: FieldOption[] = [
  { id: 'option-1', label: 'Opción 1', value: 'option_1' },
]

const createField = (
  type: FieldType,
  position: number,
  options: AddFieldOptions,
): FormField => {
  const common = {
    id: options.id,
    name: options.name ?? `${type}_${position + 1}`,
    label: options.label ?? defaultLabel(type),
    helpText: options.helpText ?? '',
    placeholder: options.placeholder ?? '',
    required: options.required ?? false,
    position,
  }

  if (type === 'select') {
    return {
      ...common,
      type,
      options: options.options ?? defaultOptions,
    }
  }

  if (type === 'number') {
    return {
      ...common,
      type,
      ...(options.min !== undefined ? { min: options.min } : {}),
      ...(options.max !== undefined ? { max: options.max } : {}),
    }
  }

  if (type === 'checkbox') {
    return { ...common, type }
  }

  return {
    ...common,
    type,
    ...(options.minLength !== undefined ? { minLength: options.minLength } : {}),
    ...(options.maxLength !== undefined ? { maxLength: options.maxLength } : {}),
  }
}

const validateAndNormalize = (form: FormDefinition): FormDefinition => {
  const normalized = normalizeFormDefinition(form)
  return formDefinitionSchema.parse(normalized)
}

const uniqueName = (form: FormDefinition, requestedName: string, ignoredFieldId?: string): string => {
  const baseName = normalizeIdentifier(requestedName) || 'field'
  const names = new Set(
    form.fields
      .filter((field) => field.id !== ignoredFieldId)
      .map((field) => field.name),
  )

  if (!names.has(baseName)) return baseName

  let suffix = 2
  while (names.has(`${baseName}_${suffix}`)) suffix += 1
  return `${baseName}_${suffix}`
}

const isTextLikeField = (field: FormField): field is Extract<FormField, { type: 'text' | 'email' | 'textarea' }> => (
  field.type === 'text' || field.type === 'email' || field.type === 'textarea'
)

export const addField = (
  form: FormDefinition,
  type: FieldType,
  options: AddFieldOptions,
): FormDefinition => {
  const nextForm = cloneFormDefinition(form)
  const field = createField(type, nextForm.fields.length, {
    ...options,
    name: uniqueName(nextForm, options.name ?? type),
  })

  nextForm.fields.push(field)
  return validateAndNormalize(nextForm)
}

export const updateField = (
  form: FormDefinition,
  fieldId: string,
  patch: FieldPatch,
): FormDefinition => {
  const nextForm = cloneFormDefinition(form)
  const fieldIndex = nextForm.fields.findIndex((field) => field.id === fieldId)
  if (fieldIndex === -1) throw new Error(`Campo no encontrado: ${fieldId}`)

  const currentField = nextForm.fields[fieldIndex]
  const nextType = patch.type ?? currentField.type
  const nextField = createField(nextType, currentField.position, {
    id: currentField.id,
    name: patch.name ?? currentField.name,
    label: patch.label ?? currentField.label,
    helpText: patch.helpText ?? currentField.helpText,
    placeholder: patch.placeholder ?? currentField.placeholder,
    required: patch.required ?? currentField.required,
    minLength: patch.minLength ?? (isTextLikeField(currentField)
      ? currentField.minLength
      : undefined),
    maxLength: patch.maxLength ?? (isTextLikeField(currentField)
      ? currentField.maxLength
      : undefined),
    min: patch.min ?? (currentField.type === 'number' ? currentField.min : undefined),
    max: patch.max ?? (currentField.type === 'number' ? currentField.max : undefined),
    options: patch.options ?? (currentField.type === 'select' ? currentField.options : undefined),
  })

  nextForm.fields[fieldIndex] = {
    ...nextField,
    name: uniqueName(nextForm, nextField.name, fieldId),
  }
  return validateAndNormalize(nextForm)
}

export const moveField = (
  form: FormDefinition,
  fieldId: string,
  targetPosition: number,
): FormDefinition => {
  if (!Number.isInteger(targetPosition) || targetPosition < 0 || targetPosition >= form.fields.length) {
    throw new Error(`Posición inválida: ${targetPosition}`)
  }

  const nextForm = cloneFormDefinition(form)
  const currentIndex = nextForm.fields.findIndex((field) => field.id === fieldId)
  if (currentIndex === -1) throw new Error(`Campo no encontrado: ${fieldId}`)

  const [field] = nextForm.fields.splice(currentIndex, 1)
  nextForm.fields.splice(targetPosition, 0, field)
  return validateAndNormalize(nextForm)
}

export const removeField = (form: FormDefinition, fieldId: string): FormDefinition => {
  const nextForm = cloneFormDefinition(form)
  const fieldIndex = nextForm.fields.findIndex((field) => field.id === fieldId)
  if (fieldIndex === -1) throw new Error(`Campo no encontrado: ${fieldId}`)

  nextForm.fields.splice(fieldIndex, 1)
  return validateAndNormalize(nextForm)
}