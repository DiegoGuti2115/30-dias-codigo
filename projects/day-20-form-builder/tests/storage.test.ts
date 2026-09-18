import { describe, expect, it } from 'vitest'

import fixture from '../data/contact-form.json'
import { formDefinitionSchema } from '../src/utils/schema'
import { createFormStorage, FORM_STORAGE_KEY, serializeFormDefinition } from '../src/utils/storage'

const form = formDefinitionSchema.parse(fixture)

const createMemoryStorage = (): Storage => {
  const values = new Map<string, string>()
  return {
    getItem: (key) => values.get(key) ?? null,
    setItem: (key, value) => { values.set(key, value) },
    removeItem: (key) => { values.delete(key) },
    clear: () => { values.clear() },
    key: (index) => [...values.keys()][index] ?? null,
    get length() { return values.size },
  }
}

describe('createFormStorage', () => {
  it('returns null when there is no saved draft and persists a validated form', () => {
    const storage = createMemoryStorage()
    const adapter = createFormStorage(storage)

    expect(adapter.read()).toBeNull()
    adapter.write(form)

    expect(storage.getItem(FORM_STORAGE_KEY)).toContain('contact-form')
    expect(adapter.read()).toEqual(form)
  })

  it('rejects malformed saved definitions instead of silently loading them', () => {
    const storage = createMemoryStorage()
    storage.setItem(FORM_STORAGE_KEY, JSON.stringify({ id: 'broken' }))

    expect(() => createFormStorage(storage).read()).toThrow()
  })

  it('propagates write failures so the hook can activate memory mode', () => {
    const storage = createMemoryStorage()
    storage.setItem = () => { throw new Error('quota exceeded') }

    expect(() => createFormStorage(storage).write(form)).toThrow('quota exceeded')
  })
})

describe('serializeFormDefinition', () => {
  it('creates stable, readable JSON from a validated form', () => {
    const serialized = serializeFormDefinition(form)

    expect(serialized).toContain('"title": "Contacto"')
    expect(() => JSON.parse(serialized)).not.toThrow()
  })
})