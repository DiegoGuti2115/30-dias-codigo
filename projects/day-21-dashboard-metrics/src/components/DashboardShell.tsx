'use client'

import { useState } from 'react'
import React from 'react'

import { selectDashboardView } from '../lib/dashboard'
import type { MetricsDashboard, PeriodId } from '../lib/types'
import { EmptyState } from './EmptyState'
import { KpiCard } from './KpiCard'
import { MetricAnalysis } from './MetricAnalysis'

const dateFormatter = new Intl.DateTimeFormat('es-ES', {
  day: 'numeric',
  month: 'long',
  year: 'numeric',
})

export function DashboardShell({ dashboard }: { dashboard: MetricsDashboard }) {
  const [periodId, setPeriodId] = useState<PeriodId>(dashboard.defaultPeriod)
  const hasMetrics = dashboard.metrics.length > 0

  if (!hasMetrics) return <main className="page-shell state-page"><EmptyState /></main>

  const view = selectDashboardView(dashboard, { periodId })

  return (
    <main className="page-shell">
      <div className="dashboard-frame">
        <header className="dashboard-header">
          <div className="brand-lockup">
            <span className="brand-dot" aria-hidden="true" />
            <span className="eyebrow">Signal Desk / Operaciones</span>
          </div>
          <div className="header-meta">
            <span className="live-status"><span className="status-dot" aria-hidden="true" />Datos locales</span>
            <span>Actualizado {dateFormatter.format(new Date(dashboard.updatedAt))}</span>
          </div>
        </header>

        <section className="hero-row" aria-labelledby="dashboard-title">
          <div>
            <p className="eyebrow hero-eyebrow">Resumen de rendimiento</p>
            <h1 id="dashboard-title">Una lectura clara<br /><em>de lo que importa.</em></h1>
            <p className="hero-copy">Indicadores esenciales para entender el pulso de tu operación sin ruido.</p>
          </div>
          <label className="period-control">
            <span>Ventana de análisis</span>
            <select value={periodId} onChange={(event) => setPeriodId(event.target.value as PeriodId)}>
              {dashboard.periods.map((period) => <option key={period.id} value={period.id}>{period.label}</option>)}
            </select>
          </label>
        </section>

        <section className="kpi-grid" aria-label="Indicadores principales">
          {dashboard.metrics.map((metric) => {
            const metricView = selectDashboardView(dashboard, { periodId, metricId: metric.id })
            return <KpiCard key={metric.id} metric={metric} variation={metricView.variation} />
          })}
        </section>

        <section className="insight-strip" aria-label="Contexto del periodo">
          <div className="insight-index">01</div>
          <div>
            <p className="eyebrow">Ventana seleccionada</p>
            <p className="insight-title">{view.period.label}</p>
          </div>
          <div className="insight-note">Las tarjetas muestran el valor actual frente al periodo de comparación.</div>
          <div className="quality-badge"><span className="status-dot" aria-hidden="true" />Calidad {dashboard.quality === 'good' ? 'verificada' : dashboard.quality}</div>
        </section>

        <MetricAnalysis dashboard={dashboard} periodId={periodId} />

        <footer className="dashboard-footer">
          <span>DAY 21 / DASHBOARD DE MÉTRICAS</span>
          <span>{dashboard.metrics.length} indicadores monitorizados</span>
        </footer>
      </div>
    </main>
  )
}