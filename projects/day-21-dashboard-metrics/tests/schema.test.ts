import { describe, expect, it } from 'vitest'

import fixture from '../data/metrics-dashboard.json'
import { metricsDashboardSchema } from '../src/lib/schema'

describe('metricsDashboardSchema', () => {
  it('acepta el fixture del dashboard', () => {
    const result = metricsDashboardSchema.safeParse(fixture)

    expect(result.success).toBe(true)
  })

  it('rechaza una unidad desconocida', () => {
    const input = structuredClone(fixture)
    input.metrics[0].unit = 'unknown'

    expect(metricsDashboardSchema.safeParse(input).success).toBe(false)
  })

  it('rechaza un periodo duplicado', () => {
    const input = structuredClone(fixture)
    input.periods[1].id = input.periods[0].id

    expect(metricsDashboardSchema.safeParse(input).success).toBe(false)
  })
})
