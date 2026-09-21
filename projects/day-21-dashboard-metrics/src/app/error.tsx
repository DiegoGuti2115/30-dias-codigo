'use client'

export default function Error({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <main className="page-shell state-page">
      <section className="state-panel" role="alert">
        <span className="eyebrow">Datos no disponibles</span>
        <h1>No hemos podido cargar las métricas.</h1>
        <p>El dataset no pudo validarse. Puedes intentar cargarlo de nuevo.</p>
        <button className="button button-primary" onClick={reset} type="button">Reintentar</button>
      </section>
    </main>
  )
}