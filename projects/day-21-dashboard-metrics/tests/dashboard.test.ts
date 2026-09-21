import { describe, expect, it } from 'vitest'

import fixture from '../data/metrics-dashboard.json'
import {
  calculateVariation,
  selectDashboardView,
} from '../src/lib/dashboard'
import { normalizeDashboard } from '../src/lib/normalize'

const dashboard = normalizeDashboard(fixture)

describe('calculateVariation', () => {
  it('calcula cambio absoluto, porcentaje y dirección ascendente', () => {
    expect(calculateVariation(120, 100)).toEqual({
      absolute: 20,
      percentage: 20,
      direction: 'up',
    })
  })

  it('calcula dirección descendente usando la magnitud del valor previo', () => {
    expect(calculateVariation(-80, -100)).toEqual({
      absolute: 20,
      percentage: 20,
      direction: 'up',
    })
    expect(calculateVariation(80, 100)).toEqual({
      absolute: -20,
      percentage: -20,
      direction: 'down',
    })
  })

  it('devuelve estado neutral cuando los valores son iguales', () => {
    expect(calculateVariation(100, 100)).toEqual({
      absolute: 0,
      percentage: 0,
      direction: 'neutral',
    })
  })

  it('devuelve estado desconocido sin comparación válida', () => {
    expect(calculateVariation(100, null)).toEqual({
      absolute: null,
      percentage: null,
      direction: 'unknown',
    })
    expect(calculateVariation(100, 0)).toEqual({
      absolute: 100,
      percentage: null,
      direction: 'unknown',
    })
  })
})

describe('selectDashboardView', () => {
  it('usa el periodo y la primera métrica por defecto', () => {
    const view = selectDashboardView(dashboard)

    expect(view.period.id).toBe('30d')
    expect(view.metric.id).toBe('active-users')
    expect(view.series).toHaveLength(7)
    expect(view.breakdown).toEqual(view.metric.breakdown)
    expect(view.variation.direction).toBe('up')
  })

  it('selecciona métrica y periodo y limita la serie a la ventana elegida', () => {
    const view = selectDashboardView(dashboard, {
      periodId: '7d',
      metricId: 'conversion-rate',
    })

    expect(view.period.id).toBe('7d')
    expect(view.metric.id).toBe('conversion-rate')
    expect(view.series).toHaveLength(7)
    expect(view.series[0].date).toBe('2026-09-13')
  })

  it('conserva el dataset de entrada sin mutarlo', () => {
    const originalSeries = dashboard.metrics[0].series.map((point) => point.date)
    const originalBreakdown = dashboard.metrics[0].breakdown.map((item) => item.id)

    const view = selectDashboardView(dashboard, { metricId: 'monthly-revenue' })
    view.series.reverse()
    view.breakdown.reverse()

    expect(dashboard.metrics[0].series.map((point) => point.date)).toEqual(originalSeries)
    expect(dashboard.metrics[0].breakdown.map((item) => item.id)).toEqual(originalBreakdown)
  })

  it('falla con una selección inexistente', () => {
    expect(() => selectDashboardView(dashboard, { metricId: 'unknown' })).toThrow('Métrica no encontrada')
    expect(() => selectDashboardView(dashboard, { periodId: '7d', metricId: 'unknown' })).toThrow()
  })
})