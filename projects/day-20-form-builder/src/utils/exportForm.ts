import { serializeFormDefinition } from './storage'
import type { FormDefinition } from './types'

export const downloadFormDefinition = (form: FormDefinition): void => {
  const blob = new Blob([serializeFormDefinition(form)], { type: 'application/json;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${form.name || 'formulario'}.json`
  link.click()
  URL.revokeObjectURL(url)
}