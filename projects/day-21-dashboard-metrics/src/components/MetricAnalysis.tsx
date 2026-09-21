'use client'

import { useEffect, useState } from 'react'
import React from 'react'
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { selectDashboardView } from '../lib/dashboard'
import type { MetricsDashboard, MetricPoint, PeriodId } from '../lib/types'
import { MetricSelector } from './MetricSelector'

const dateFormatter = new Intl.DateTimeFormat('es-ES', { day: 'numeric', month: 'short' })

const formatPointValue = (value: number) => new Intl.NumberFormat('es-ES', {
  maximumFractionDigits: value < 10 ? 1 : 0,
}).format(value)

const toDate = (date: string) => new Date(`${date}T00:00:00.000Z`)

function SelectedPoint({ point, metric }: { point: MetricPoint; metric: MetricsDashboard['metrics'][number] }) {
  return (
    <div className="selected-point" aria-live="polite">
      <div>
        <p className="eyebrow">Punto seleccionado</p>
        <p className="selected-date">{dateFormatter.format(toDate(point.date))}</p>
      </div>
      <strong>{formatPointValue(point.value)}{metric.unit === 'percentage' ? '%' : metric.unit === 'currency' ? ' €' : metric.unit === 'duration' ? ' min' : ''}</strong>
    </div>
  )
}

function Breakdown({ metric }: { metric: MetricsDashboard['metrics'][number] }) {
  const total = metric.breakdown.reduce((sum, item) => sum + item.value, 0)

  return (
    <section className="breakdown-panel" aria-labelledby="breakdown-title">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Distribución</p>
          <h3 id="breakdown-title">Por categoría</h3>
        </div>
        <span className="panel-count">{metric.breakdown.length} grupos</span>
      </div>
      <div className="breakdown-list">
        {metric.breakdown.map((item) => {
          const share = total === 0 ? 0 : (item.value / total) * 100
          return (
            <div className="breakdown-item" key={item.id}>
              <div className="breakdown-label"><span>{item.label}</span><strong>{formatPointValue(item.value)}</strong></div>
              <div className="breakdown-track"><span style={{ width: `${share}%` }} /></div>
            </div>
          )
        })}
      </div>
    </section>
  )
}

export function MetricAnalysis({ dashboard, periodId }: { dashboard: MetricsDashboard; periodId: PeriodId }) {
  const [metricId, setMetricId] = useState(dashboard.metrics[0]?.id ?? '')
  const view = selectDashboardView(dashboard, { metricId, periodId })
  const [selectedDate, setSelectedDate] = useState(view.series.at(-1)?.date ?? '')
  const selectedPoint = view.series.find((point) => point.date === selectedDate) ?? view.series.at(-1)

  useEffect(() => {
    setSelectedDate(view.series.at(-1)?.date ?? '')
  }, [metricId, periodId, view.series])

  if (!selectedPoint) return null

  return (
    <section className="analysis-section" aria-labelledby="analysis-title">
      <div className="analysis-heading">
        <div>
          <p className="eyebrow">02 / Exploración</p>
          <h2 id="analysis-title">Sigue el movimiento.</h2>
          <p className="analysis-copy">Selecciona un indicador y consulta su evolución sin perder el contexto.</p>
        </div>
        <MetricSelector metrics={dashboard.metrics} onChange={setMetricId} selectedMetricId={metricId} />
      </div>

      <div className="analysis-grid">
        <section className="chart-panel" aria-labelledby="series-title">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Serie temporal</p>
              <h3 id="series-title">{view.metric.label}</h3>
            </div>
            <span className="panel-count">{view.period.label}</span>
          </div>
          <div className="chart-wrap">
            <ResponsiveContainer height="100%" width="100%">
              <LineChart data={view.series} margin={{ top: 12, right: 12, bottom: 4, left: -18 }} onClick={(state) => {
                const point = state?.activePayload?.[0]?.payload as MetricPoint | undefined
                if (point) setSelectedDate(point.date)
              }}>
                <CartesianGrid stroke="var(--line)" strokeDasharray="2 5" vertical={false} />
                <XAxis axisLine={false} dataKey="date" tick={{ fill: 'var(--muted)', fontSize: 11 }} tickFormatter={(date) => dateFormatter.format(toDate(date))} tickLine={false} />
                <YAxis axisLine={false} tick={{ fill: 'var(--muted)', fontSize: 11 }} tickLine={false} width={48} />
                <Tooltip
                  contentStyle={{ background: 'var(--ink)', border: 0, borderRadius: 0, color: 'white', fontSize: 12 }}
                  labelFormatter={(date) => dateFormatter.format(toDate(String(date)))}
                  formatter={(value) => [formatPointValue(Number(value)), view.metric.label]}
                />
                <Line activeDot={{ fill: 'var(--accent)', r: 6, stroke: 'var(--card)', strokeWidth: 3 }} dataKey="value" dot={{ fill: 'var(--deep-mint)', r: 3, strokeWidth: 0 }} isAnimationActive={false} stroke="var(--deep-mint)" strokeWidth={2.5} type="monotone" />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <SelectedPoint metric={view.metric} point={selectedPoint} />
        </section>

        <Breakdown metric={view.metric} />
      </div>

      <details className="data-table-disclosure">
        <summary>Ver datos de la serie en tabla</summary>
        <div className="data-table-wrap">
          <table className="data-table">
            <caption className="sr-only">Valores diarios de {view.metric.label}</caption>
            <thead><tr><th scope="col">Fecha</th><th scope="col">Valor</th><th scope="col">Estado</th></tr></thead>
            <tbody>{view.series.map((point) => <tr key={point.date}><th scope="row">{dateFormatter.format(toDate(point.date))}</th><td>{formatPointValue(point.value)}</td><td>{point.date === selectedPoint.date ? 'Seleccionado' : 'Disponible'}</td></tr>)}</tbody>
          </table>
        </div>
      </details>
    </section>
  )
}