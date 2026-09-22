// tests/examples.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { fetchExamples } from '../src/lib/examples'

const mockFetch = vi.fn()
vi.stubGlobal('fetch', mockFetch)

const validExample = {
  method: 'GET',
  url: 'http://localhost:3000/api/mock/profile',
  query: [],
  headers: [],
  bodyFormat: 'none',
  body: '',
}

beforeEach(() => mockFetch.mockReset())

describe('fetchExamples', () => {
  it('devuelve ejemplos válidos cuando la respuesta es ok', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => [validExample],
    })
    const result = await fetchExamples('/api/mock/examples')
    expect(result).toHaveLength(1)
    expect(result[0].method).toBe('GET')
  })

  it('lanza error si la respuesta no es ok', async () => {
    mockFetch.mockResolvedValue({ ok: false, status: 500, json: async () => [] })
    await expect(fetchExamples('/api/mock/examples')).rejects.toThrow('500')
  })

  it('lanza error si el cuerpo no es un array', async () => {
    mockFetch.mockResolvedValue({ ok: true, json: async () => ({ data: [] }) })
    await expect(fetchExamples('/api/mock/examples')).rejects.toThrow('Formato')
  })

  it('lanza error si un ejemplo no pasa la validación Zod', async () => {
    mockFetch.mockResolvedValue({ ok: true, json: async () => [{ method: 'INVALID' }] })
    await expect(fetchExamples('/api/mock/examples')).rejects.toThrow()
  })
})