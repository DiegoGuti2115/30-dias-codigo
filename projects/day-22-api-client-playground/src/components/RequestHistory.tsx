import type { RequestHistoryEntry } from '../lib/types'

type RequestHistoryProps = {
  entries: RequestHistoryEntry[]
  onClear: () => void
  onRemove: (id: string) => void
  onRestore: (entry: RequestHistoryEntry) => void
}

const formatTimestamp = (value: string) => new Intl.DateTimeFormat('es-ES', {
  dateStyle: 'short', timeStyle: 'short',
}).format(new Date(value))

export function RequestHistory({ entries, onClear, onRemove, onRestore }: RequestHistoryProps) {
  return (
    <section aria-labelledby="history-title" className="request-history">
      <div className="response-heading">
        <h2 id="history-title">Solicitudes recientes</h2>
        {entries.length > 0 && <button className="secondary-button" onClick={onClear} type="button">Limpiar historial</button>}
      </div>
      {entries.length === 0 ? <p>No hay solicitudes recientes guardadas localmente.</p> : (
        <ol className="history-list">
          {entries.map((entry) => (
            <li key={entry.id}>
              <button className="history-entry" onClick={() => onRestore(entry)} type="button">
                <strong>{entry.request.method}</strong><span>{entry.request.url}</span><small>{formatTimestamp(entry.createdAt)}</small>
              </button>
              <button aria-label={`Eliminar ${entry.request.method} ${entry.request.url} del historial`} className="secondary-button" onClick={() => onRemove(entry.id)} type="button">Eliminar</button>
            </li>
          ))}
        </ol>
      )}
      <p className="history-note">El historial es local, limitado y no guarda cuerpos ni cabeceras sensibles.</p>
    </section>
  )
}
