import examples from '../data/request-examples.json'
import { sanitizeRequestForHistory, serializeRequest } from '../src/lib/request'
import { apiRequestDraftSchema } from '../src/lib/schema'

import { describe, expect, it } from 'vitest'

describe('request helpers', () => {
  it('elimina secretos del historial sin mutar la solicitud', () => {
    const request = apiRequestDraftSchema.parse(structuredClone(examples[0]))
    request.headers.push({ key: 'Authorization', value: 'Bearer secret', enabled: true })
    request.headers.push({ key: 'X-Api-Key', value: 'secret', enabled: true })

    const sanitized = sanitizeRequestForHistory(request)

    expect(sanitized.headers.map((header) => header.key)).toEqual(['Accept'])
    expect(sanitized.body).toBe('')
    expect(sanitized.bodyFormat).toBe('none')
    expect(request.headers).toHaveLength(3)
  })

  it('serializa solo los pares activos y normaliza espacios en las claves', () => {
    const request = apiRequestDraftSchema.parse(structuredClone(examples[0]))
    request.query.push({ key: 'unused', value: 'no', enabled: false })
    request.headers[0].key = ' Accept '

    expect(JSON.parse(serializeRequest(request))).toMatchObject({
      query: [{ key: 'include', value: 'preferences' }],
      headers: [{ key: 'Accept', value: 'application/json' }],
    })
  })
})
