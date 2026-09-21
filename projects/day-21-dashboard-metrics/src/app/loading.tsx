export default function Loading() {
  return (
    <main className="page-shell" aria-busy="true" aria-live="polite">
      <div className="loading-layout">
        <div className="skeleton skeleton-kicker" />
        <div className="skeleton skeleton-title" />
        <div className="skeleton-grid">
          {[1, 2, 3, 4].map((item) => <div className="skeleton skeleton-card" key={item} />)}
        </div>
      </div>
    </main>
  )
}