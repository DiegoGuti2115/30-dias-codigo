import { formDefinitionSchema } from './schema'
import type { FormDefinition } from './types'

export const FORM_STORAGE_KEY = 'day-20-form-builder:draft:v1'

export interface FormStorage {
  read: () => FormDefinition | null
  write: (form: FormDefinition) => void
}

const browserStorage = (): Storage => {
  if (typeof window === 'undefined' || !window.localStorage) {
    throw new Error('El almacenamiento local no está disponible')
  }
  return window.localStorage
}

export const createFormStorage = (storage: Storage = browserStorage()): FormStorage => ({
  read: () => {
    const raw = storage.getItem(FORM_STORAGE_KEY)
    if (!raw) return null
    return formDefinitionSchema.parse(JSON.parse(raw))
  },
  write: (form) => {
    const validated = formDefinitionSchema.parse(form)
    storage.setItem(FORM_STORAGE_KEY, JSON.stringify(validated))
  },
})

export const serializeFormDefinition = (form: FormDefinition): string => (
  JSON.stringify(formDefinitionSchema.parse(form), null, 2)
)