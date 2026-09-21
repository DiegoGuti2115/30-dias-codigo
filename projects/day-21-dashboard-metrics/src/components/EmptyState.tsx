import React from 'react'

export function EmptyState() {
  return (
    <section className="state-panel" aria-live="polite">
      <span className="eyebrow">Sin resultados</span>
      <h2>No hay métricas para este periodo.</h2>
      <p>Selecciona otra ventana temporal para volver a consultar la actividad.</p>
    </section>
  )
}