import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import React from 'react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import fixture from '../data/metrics-dashboard.json'
import { normalizeDashboard } from '../src/lib/normalize'
import { MetricAnalysis } from '../src/components/MetricAnalysis'

vi.mock('recharts', () => ({
  CartesianGrid: () => null,
  Line: () => null,
  LineChart: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Tooltip: () => null,
  XAxis: () => null,
  YAxis: () => null,
}))

const dashboard = normalizeDashboard(fixture)

afterEach(() => {
  cleanup()
})

describe('MetricAnalysis', () => {
  it('permite cambiar la métrica con controles accesibles', () => {
    render(<MetricAnalysis dashboard={dashboard} periodId="30d" />)

    expect(screen.getByRole('heading', { name: 'Usuarios activos' })).toBeTruthy()
    fireEvent.click(screen.getByRole('button', { name: 'Conversión' }))

    expect(screen.getByRole('heading', { name: 'Conversión' })).toBeTruthy()
    expect(screen.getByRole('button', { name: 'Conversión' }).getAttribute('aria-pressed')).toBe('true')
  })

  it('ofrece una alternativa tabular y un punto seleccionado visible', () => {
    render(<MetricAnalysis dashboard={dashboard} periodId="7d" />)

    expect(screen.getByText('Ver datos de la serie en tabla')).toBeTruthy()
    expect(screen.getByText('Punto seleccionado')).toBeTruthy()
    expect(screen.getAllByText('19 sept').length).toBeGreaterThan(0)
  })
})