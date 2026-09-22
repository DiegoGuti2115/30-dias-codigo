import examples from '../data/request-examples.json'
import { apiRequestDraftSchema, requestHistorySchema } from '../src/lib/schema'
import { MAX_BODY_BYTES, MAX_HISTORY_ENTRIES } from '../src/lib/types'

import { describe, expect, it } from 'vitest'

describe('apiRequestDraftSchema', () => {
  it('acepta las solicitudes de ejemplo', () => {
    expect(apiRequestDraftSchema.safeParse(examples[0]).success).toBe(true)
    expect(apiRequestDraftSchema.safeParse(examples[1]).success).toBe(true)
  })

  it('rechaza URL no HTTP, JSON inválido y cabeceras duplicadas', () => {
    const invalid = structuredClone(examples[1])
    invalid.url = 'ftp://example.test/resource'
    invalid.body = '{'
    invalid.headers.push({ key: 'content-type', value: 'text/plain', enabled: true })

    expect(apiRequestDraftSchema.safeParse(invalid).success).toBe(false)
  })

  it('rechaza parámetros activos sin nombre y cuerpos por encima del límite', () => {
    const invalid = structuredClone(examples[0])
    invalid.query = [{ key: '', value: 'value', enabled: true }]
    invalid.bodyFormat = 'json'
    invalid.body = 'x'.repeat(MAX_BODY_BYTES + 1)

    expect(apiRequestDraftSchema.safeParse(invalid).success).toBe(false)
  })

  it('limita el historial', () => {
    const item = {
      id: 'f2f13104-50e8-472b-a5d4-f8414f3d27ca',
      createdAt: '2026-09-21T10:00:00.000Z',
      request: examples[0],
    }

    expect(requestHistorySchema.safeParse(Array.from({ length: MAX_HISTORY_ENTRIES }, () => item)).success).toBe(true)
    expect(requestHistorySchema.safeParse(Array.from({ length: MAX_HISTORY_ENTRIES + 1 }, () => item)).success).toBe(false)
  })
})