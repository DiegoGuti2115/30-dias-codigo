export const FIELD_TYPES = [
  'text',
  'email',
  'number',
  'textarea',
  'select',
  'checkbox',
] as const

export type FieldType = (typeof FIELD_TYPES)[number]

export interface FieldOption {
  id: string
  label: string
  value: string
}

interface CommonField {
  id: string
  name: string
  label: string
  helpText: string
  placeholder: string
  required: boolean
  position: number
}

interface TextLikeField extends CommonField {
  type: 'text' | 'email' | 'textarea'
  minLength?: number
  maxLength?: number
}

interface NumberField extends CommonField {
  type: 'number'
  min?: number
  max?: number
}

export interface SelectField extends CommonField {
  type: 'select'
  options: FieldOption[]
}

export interface CheckboxField extends CommonField {
  type: 'checkbox'
}

export type FormField = TextLikeField | NumberField | SelectField | CheckboxField

export interface FormDefinition {
  id: string
  name: string
  title: string
  description: string
  fields: FormField[]
}