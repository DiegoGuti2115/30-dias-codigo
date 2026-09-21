import React from 'react'
import type { DashboardMetric, MetricVariation } from '../lib/types'

const numberFormatters: Record<DashboardMetric['unit'], Intl.NumberFormatOptions> = {
  count: { maximumFractionDigits: 0 },
  percentage: { maximumFractionDigits: 1 },
  currency: { maximumFractionDigits: 0 },
  duration: { maximumFractionDigits: 0 },
}

const formatValue = (metric: DashboardMetric) => {
  const value = new Intl.NumberFormat('es-ES', numberFormatters[metric.unit]).format(metric.currentValue)
  if (metric.unit === 'percentage') return `${value}%`
  if (metric.unit === 'currency') return `${value} €`
  if (metric.unit === 'duration') return `${value} min`
  return value
}

const formatPercentage = (value: number | null) => (
  value === null ? 'Sin base de comparación' : `${value > 0 ? '+' : ''}${value.toFixed(1)}%`
)

const getTrendLabel = (variation: MetricVariation) => {
  if (variation.direction === 'unknown') return 'Sin comparación'
  if (variation.direction === 'neutral') return 'Sin cambios'
  return variation.direction === 'up' ? 'En aumento' : 'En descenso'
}

export function KpiCard({ metric, variation }: { metric: DashboardMetric; variation: MetricVariation }) {
  return (
    <article className="kpi-card">
      <div className="kpi-heading">
        <span className="kpi-label">{metric.label}</span>
        <span className="kpi-mark" aria-hidden="true">{metric.unit === 'currency' ? '€' : metric.unit === 'percentage' ? '%' : metric.unit === 'duration' ? '◷' : '∿'}</span>
      </div>
      <p className="kpi-value">{formatValue(metric)}</p>
      <div className={`kpi-trend trend-${variation.direction}`}>
        <span aria-hidden="true">{variation.direction === 'up' ? '↗' : variation.direction === 'down' ? '↘' : variation.direction === 'neutral' ? '→' : '·'}</span>
        <span>{formatPercentage(variation.percentage)}</span>
        <span className="sr-only">{getTrendLabel(variation)}</span>
      </div>
      <p className="kpi-description">{metric.description}</p>
    </article>
  )
}