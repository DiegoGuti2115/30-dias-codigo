import type { FormDefinition, FormField } from './types'

export type FormResponseValue = string | number | boolean | undefined
export type FormResponse = Record<string, FormResponseValue>
export type ValidationErrors = Record<string, string>

export interface ValidationResult {
  success: boolean
  errors: ValidationErrors
  values: FormResponse
}

const isEmpty = (value: FormResponseValue): boolean => value === undefined || value === null || value === ''

const addError = (errors: ValidationErrors, field: FormField, message: string): void => {
  if (!errors[field.id]) errors[field.id] = message
}

const validateTextLike = (
  field: Extract<FormField, { type: 'text' | 'email' | 'textarea' }>,
  value: FormResponseValue,
  errors: ValidationErrors,
): void => {
  if (isEmpty(value)) return
  if (typeof value !== 'string') {
    addError(errors, field, 'Introduce un texto válido.')
    return
  }
  if (field.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
    addError(errors, field, 'Introduce un correo electrónico válido.')
  }
  if (field.minLength !== undefined && value.length < field.minLength) {
    addError(errors, field, `Escribe al menos ${field.minLength} caracteres.`)
  }
  if (field.maxLength !== undefined && value.length > field.maxLength) {
    addError(errors, field, `No superes los ${field.maxLength} caracteres.`)
  }
}

const validateNumber = (
  field: Extract<FormField, { type: 'number' }>,
  value: FormResponseValue,
  errors: ValidationErrors,
): number | undefined => {
  if (isEmpty(value)) return undefined
  const parsed = typeof value === 'number' ? value : Number(value)
  if (!Number.isFinite(parsed)) {
    addError(errors, field, 'Introduce un número válido.')
    return undefined
  }
  if (field.min !== undefined && parsed < field.min) addError(errors, field, `El valor mínimo es ${field.min}.`)
  if (field.max !== undefined && parsed > field.max) addError(errors, field, `El valor máximo es ${field.max}.`)
  return parsed
}

export const validateFormResponse = (form: FormDefinition, response: FormResponse): ValidationResult => {
  const errors: ValidationErrors = {}
  const values: FormResponse = { ...response }

  for (const field of form.fields) {
    const value = response[field.name]
    if (field.required && (field.type === 'checkbox' ? value !== true : isEmpty(value))) {
      addError(errors, field, field.type === 'checkbox' ? 'Debes aceptar esta opción.' : 'Este campo es obligatorio.')
      continue
    }

    if (field.type === 'text' || field.type === 'email' || field.type === 'textarea') {
      validateTextLike(field, value, errors)
    } else if (field.type === 'number') {
      const parsed = validateNumber(field, value, errors)
      if (parsed !== undefined) values[field.name] = parsed
    } else if (field.type === 'select' && !isEmpty(value) && !field.options.some((option) => option.value === value)) {
      addError(errors, field, 'Selecciona una opción válida.')
    } else if (field.type === 'checkbox' && value !== undefined && typeof value !== 'boolean') {
      addError(errors, field, 'El valor debe ser una casilla.')
    }
  }

  return { success: Object.keys(errors).length === 0, errors, values }
}