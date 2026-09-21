import { describe, expect, it, vi } from 'vitest'

import fixture from '../data/metrics-dashboard.json'
import { createHttpDashboardSource, loadDashboard } from '../src/lib/dataSource'

describe('dashboard data sources', () => {
  it('carga y valida una fuente HTTP correcta', async () => {
    const request = vi.fn().mockResolvedValue(new Response(JSON.stringify(fixture), {
      headers: { 'content-type': 'application/json' },
      status: 200,
    }))

    const dashboard = await loadDashboard(createHttpDashboardSource('/metrics.json', request))

    expect(request).toHaveBeenCalledWith('/metrics.json', { headers: { accept: 'application/json' } })
    expect(dashboard.metrics).toHaveLength(4)
  })

  it('usa el fallback local si la fuente HTTP responde con error', async () => {
    const request = vi.fn().mockResolvedValue(new Response('unavailable', { status: 503 }))

    const dashboard = await loadDashboard(createHttpDashboardSource('/metrics.json', request))

    expect(dashboard.version).toBe('1.0.0')
    expect(dashboard.quality).toBe('good')
  })

  it('usa el fallback si la respuesta remota tiene datos inválidos', async () => {
    const invalidSource = { load: async () => ({ invalid: true }) }
    const fallback = { load: async () => fixture }

    const dashboard = await loadDashboard(invalidSource, fallback)

    expect(dashboard.metrics[0].id).toBe('active-users')
  })
})
