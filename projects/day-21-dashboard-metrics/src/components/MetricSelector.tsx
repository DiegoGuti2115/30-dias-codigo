import React from 'react'
import type { DashboardMetric } from '../lib/types'

export function MetricSelector({
  metrics,
  selectedMetricId,
  onChange,
}: {
  metrics: DashboardMetric[]
  selectedMetricId: string
  onChange: (metricId: string) => void
}) {
  return (
    <div className="metric-selector" role="group" aria-label="Métrica de la serie temporal">
      {metrics.map((metric) => (
        <button
          aria-pressed={metric.id === selectedMetricId}
          className={`metric-option ${metric.id === selectedMetricId ? 'metric-option-active' : ''}`}
          key={metric.id}
          onClick={() => onChange(metric.id)}
          type="button"
        >
          {metric.label}
        </button>
      ))}
    </div>
  )
}