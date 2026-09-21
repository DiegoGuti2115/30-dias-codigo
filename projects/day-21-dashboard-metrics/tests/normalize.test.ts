import { describe, expect, it } from 'vitest'

import fixture from '../data/metrics-dashboard.json'
import { normalizeDashboard } from '../src/lib/normalize'

const cloneFixture = () => structuredClone(fixture)

describe('normalizeDashboard', () => {
  it('valida el fixture y ordena periodos, series y desgloses', () => {
    const dashboard = normalizeDashboard(cloneFixture())

    expect(dashboard.periods.map((period) => period.id)).toEqual(['7d', '30d', '90d'])
    expect(dashboard.metrics[0].series.map((point) => point.date)).toEqual([
      '2026-09-13',
      '2026-09-14',
      '2026-09-15',
      '2026-09-16',
      '2026-09-17',
      '2026-09-18',
      '2026-09-19',
    ])
    expect(dashboard.metrics[0].breakdown.map((item) => item.id)).toEqual(['web', 'mobile', 'tablet'])
  })

  it('no muta la entrada original', () => {
    const input = cloneFixture()
    const originalSeries = input.metrics[0].series.map((point) => point.date)

    normalizeDashboard(input)

    expect(input.metrics[0].series.map((point) => point.date)).toEqual(originalSeries)
  })

  it('rechaza fechas de calendario imposibles', () => {
    const input = cloneFixture()
    input.metrics[0].series[0].date = '2026-02-30'

    expect(() => normalizeDashboard(input)).toThrow()
  })

  it('rechaza valores no finitos', () => {
    const input = cloneFixture()
    input.metrics[0].currentValue = Number.NaN

    expect(() => normalizeDashboard(input)).toThrow()
  })

  it('rechaza IDs duplicados en métricas, series y desgloses', () => {
    const duplicateMetric = cloneFixture()
    duplicateMetric.metrics.push(cloneFixture().metrics[0])

    const duplicateBreakdown = cloneFixture()
    duplicateBreakdown.metrics[0].breakdown.push({ id: 'web', label: 'Otra', value: 1 })

    const duplicateSeriesDate = cloneFixture()
    duplicateSeriesDate.metrics[0].series.push({ date: '2026-09-19', value: 1 })

    expect(() => normalizeDashboard(duplicateMetric)).toThrow()
    expect(() => normalizeDashboard(duplicateBreakdown)).toThrow()
    expect(() => normalizeDashboard(duplicateSeriesDate)).toThrow()
  })

  it('rechaza un periodo por defecto que no existe', () => {
    const input = cloneFixture()
    input.defaultPeriod = '7d'
    input.periods = input.periods.filter((period) => period.id !== '7d')

    expect(() => normalizeDashboard(input)).toThrow()
  })
})
