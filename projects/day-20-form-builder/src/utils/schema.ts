import { z } from 'zod'

import { FIELD_TYPES } from './types'

const identifierPattern = /^[a-z][a-z0-9_]*$/

const commonFieldSchema = z.object({
  id: z.string().trim().min(1),
  name: z.string().trim().regex(identifierPattern),
  label: z.string().trim().min(1),
  helpText: z.string(),
  placeholder: z.string(),
  required: z.boolean(),
  position: z.number().int().nonnegative(),
})

const textLikeFieldSchema = commonFieldSchema.extend({
  type: z.enum(['text', 'email', 'textarea']),
  minLength: z.number().int().nonnegative().optional(),
  maxLength: z.number().int().nonnegative().optional(),
}).superRefine((field, context) => {
  if (field.minLength !== undefined && field.maxLength !== undefined && field.minLength > field.maxLength) {
    context.addIssue({
      code: 'custom',
      path: ['maxLength'],
      message: 'maxLength debe ser mayor o igual que minLength',
    })
  }
})

const numberFieldSchema = commonFieldSchema.extend({
  type: z.literal('number'),
  min: z.number().optional(),
  max: z.number().optional(),
}).superRefine((field, context) => {
  if (field.min !== undefined && field.max !== undefined && field.min > field.max) {
    context.addIssue({
      code: 'custom',
      path: ['max'],
      message: 'max debe ser mayor o igual que min',
    })
  }
})

const optionSchema = z.object({
  id: z.string().trim().min(1),
  label: z.string().trim().min(1),
  value: z.string().trim().min(1),
})

const selectFieldSchema = commonFieldSchema.extend({
  type: z.literal('select'),
  options: z.array(optionSchema).min(1),
}).superRefine((field, context) => {
  const values = field.options.map((option) => option.value)
  if (new Set(values).size !== values.length) {
    context.addIssue({
      code: 'custom',
      path: ['options'],
      message: 'Las opciones no pueden repetir value',
    })
  }
})

const checkboxFieldSchema = commonFieldSchema.extend({
  type: z.literal('checkbox'),
})

export const formFieldSchema = z.discriminatedUnion('type', [
  textLikeFieldSchema,
  numberFieldSchema,
  selectFieldSchema,
  checkboxFieldSchema,
])

export const formDefinitionSchema = z.object({
  id: z.string().trim().min(1),
  name: z.string().trim().regex(identifierPattern),
  title: z.string().trim().min(1),
  description: z.string(),
  fields: z.array(formFieldSchema),
}).superRefine((form, context) => {
  const ids = form.fields.map((field) => field.id)
  const names = form.fields.map((field) => field.name)

  if (new Set(ids).size !== ids.length) {
    context.addIssue({
      code: 'custom',
      path: ['fields'],
      message: 'Los IDs de los campos deben ser únicos',
    })
  }

  if (new Set(names).size !== names.length) {
    context.addIssue({
      code: 'custom',
      path: ['fields'],
      message: 'Los nombres internos deben ser únicos',
    })
  }
})

export type FormDefinitionInput = z.input<typeof formDefinitionSchema>
export type ValidatedFormDefinition = z.infer<typeof formDefinitionSchema>

export { FIELD_TYPES }