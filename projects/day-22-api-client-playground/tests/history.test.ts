import examples from '../data/request-examples.json'
import { appendHistoryEntry, HISTORY_STORAGE_KEY, readHistory, writeHistory } from '../src/lib/history'
import { apiRequestDraftSchema } from '../src/lib/schema'
import { MAX_HISTORY_ENTRIES, type RequestHistoryEntry } from '../src/lib/types'

import { describe, expect, it } from 'vitest'

const createStorage = () => {
  const values = new Map<string, string>()
  return {
    getItem: (key: string) => values.get(key) ?? null,
    setItem: (key: string, value: string) => values.set(key, value),
  }
}

describe('history', () => {
  it('limita entradas y elimina cabeceras sensibles y cuerpos', () => {
    const request = apiRequestDraftSchema.parse(structuredClone(examples[1]))
    request.headers.push({ key: 'Authorization', value: 'secret', enabled: true })
    const entries = Array.from({ length: MAX_HISTORY_ENTRIES + 1 }).reduce<RequestHistoryEntry[]>((history, _, index) => appendHistoryEntry(
      history,
      request,
      `00000000-0000-4000-8000-${String(index).padStart(12, '0')}`,
      '2026-09-22T10:00:00.000Z',
    ), [])

    expect(entries).toHaveLength(MAX_HISTORY_ENTRIES)
    expect(entries[0].request.headers.map((header) => header.key)).toEqual(['Content-Type'])
    expect(entries[0].request.body).toBe('')
  })

  it('persiste solo historial válido y tolera datos corruptos', () => {
    const storage = createStorage()
    const request = apiRequestDraftSchema.parse(structuredClone(examples[0]))
    const entries = appendHistoryEntry([], request, '00000000-0000-4000-8000-000000000001', '2026-09-22T10:00:00.000Z')

    expect(writeHistory(storage, entries)).toBe(true)
    expect(readHistory(storage)).toEqual(entries)
    storage.setItem(HISTORY_STORAGE_KEY, '{broken')
    expect(readHistory(storage)).toEqual([])
  })
})
