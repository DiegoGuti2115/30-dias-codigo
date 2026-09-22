import examples from '../data/request-examples.json'
import { buildFetchOptions, buildRequestUrl, executeRequest } from '../src/lib/client'
import { apiRequestDraftSchema } from '../src/lib/schema'

import { afterEach, describe, expect, it, vi } from 'vitest'

const exampleRequest = () => apiRequestDraftSchema.parse(structuredClone(examples[1]))

describe('client', () => {
  afterEach(() => vi.useRealTimers())

  it('construye URL y opciones sin credenciales', () => {
    const request = apiRequestDraftSchema.parse(structuredClone(examples[0]))
    request.query.push({ key: 'page', value: '2', enabled: true })

    expect(buildRequestUrl(request)).toBe('http://localhost:3000/api/mock/profile?include=preferences&page=2')

    const options = buildFetchOptions(exampleRequest())
    expect(options.method).toBe('POST')
    expect(options.credentials).toBe('omit')
    expect(options.body).toContain('Hola desde el playground')
    expect(new Headers(options.headers).get('content-type')).toBe('application/json')
  })

  it('formatea JSON y conserva una respuesta HTTP fallida', async () => {
    const fetchImplementation = vi.fn().mockResolvedValue(new Response('{"error":"unavailable"}', {
      status: 503,
      statusText: 'Service Unavailable',
      headers: { 'content-type': 'application/json', 'x-trace': 'demo' },
    }))

    const result = await executeRequest(exampleRequest(), { fetchImplementation, now: () => 12 })

    expect(result).toMatchObject({
      kind: 'response',
      isHttpError: true,
      response: { status: 503, bodyKind: 'json', body: '{\n  "error": "unavailable"\n}' },
    })
  })

  it('distingue un error de red', async () => {
    const result = await executeRequest(exampleRequest(), {
      fetchImplementation: vi.fn().mockRejectedValue(new TypeError('Failed to fetch')),
    })

    expect(result).toEqual({ kind: 'network-error', message: 'Failed to fetch' })
  })

  it('distingue timeout y cancelación', async () => {
    vi.useFakeTimers()
    const pendingFetch = vi.fn((_url: string, init?: RequestInit) => new Promise<Response>((_resolve, reject) => {
      init?.signal?.addEventListener('abort', () => reject(new DOMException('aborted', 'AbortError')), { once: true })
    }))

    const timeoutResult = executeRequest(exampleRequest(), { fetchImplementation: pendingFetch, timeoutMs: 10 })
    await vi.advanceTimersByTimeAsync(10)
    await expect(timeoutResult).resolves.toMatchObject({ kind: 'timeout' })

    const controller = new AbortController()
    const abortedResult = executeRequest(exampleRequest(), { fetchImplementation: pendingFetch, signal: controller.signal })
    controller.abort()
    await expect(abortedResult).resolves.toEqual({ kind: 'aborted', message: 'La solicitud fue cancelada.' })
  })
})
