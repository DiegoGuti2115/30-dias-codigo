import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import React from 'react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import fixture from '../data/metrics-dashboard.json'
import { DashboardShell } from '../src/components/DashboardShell'
import { normalizeDashboard } from '../src/lib/normalize'

vi.mock('../src/components/MetricAnalysis', () => ({
  MetricAnalysis: () => <div data-testid="metric-analysis" />,
}))

const dashboard = normalizeDashboard(fixture)

afterEach(() => cleanup())

describe('DashboardShell', () => {
  it('cambia el periodo y conserva el contexto visible', () => {
    render(<DashboardShell dashboard={dashboard} />)

    fireEvent.change(screen.getByRole('combobox', { name: 'Ventana de análisis' }), { target: { value: '7d' } })

    expect(screen.getByText('Últimos 7 días', { selector: '.insight-title' })).toBeTruthy()
    expect(screen.getByTestId('metric-analysis')).toBeTruthy()
  })

  it('muestra un estado vacío cuando no hay métricas', () => {
    render(<DashboardShell dashboard={{ ...dashboard, metrics: [] }} />)

    expect(screen.getByRole('heading', { name: 'No hay métricas para este periodo.' })).toBeTruthy()
  })
})
