import { createEmptyRequestDraft, getDraftErrors } from '../src/lib/request-draft'

import { describe, expect, it } from 'vitest'

describe('request draft helpers', () => {
  it('crea un borrador GET seguro y vacío', () => {
    expect(createEmptyRequestDraft()).toEqual({
      method: 'GET', url: '', query: [], headers: [], bodyFormat: 'none', body: '',
    })
  })

  it('expone los errores por campo para que la interfaz los anuncie', () => {
    const errors = getDraftErrors({
      ...createEmptyRequestDraft(),
      url: 'not a url',
      query: [{ key: '', value: 'value', enabled: true }],
    })

    expect(errors.url).toBe('La URL no es válida')
    expect(errors['query.0.key']).toBe('El parámetro debe tener nombre')
  })
})
