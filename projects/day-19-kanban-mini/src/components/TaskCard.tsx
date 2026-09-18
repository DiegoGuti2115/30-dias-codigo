import type { Card, Column, ColumnId } from '../utils/types'

interface TaskCardProps {
  card: Card
  columns: Column[]
  onEdit: (card: Card) => void
  onDelete: (cardId: string) => void
  onMove: (cardId: string, columnId: ColumnId) => void
}

export function TaskCard({ card, columns, onEdit, onDelete, onMove }: TaskCardProps) {
  return (
    <article className="task-card">
      <div className="task-card-topline">
        <span className="task-dot" aria-hidden="true" />
        <span className="task-id">{card.id}</span>
      </div>
      <h3>{card.title}</h3>
      {card.description && <p>{card.description}</p>}
      <div className="task-card-footer">
        <label className="move-control">
          <span>Mover a</span>
          <select
            aria-label={`Mover ${card.title}`}
            value={card.columnId}
            onChange={(event) => onMove(card.id, event.target.value as ColumnId)}
          >
            {columns.map((column) => <option key={column.id} value={column.id}>{column.title}</option>)}
          </select>
        </label>
        <div className="task-actions">
          <button className="text-button" type="button" onClick={() => onEdit(card)}>Editar</button>
          <button className="text-button text-button-danger" type="button" onClick={() => onDelete(card.id)}>Eliminar</button>
        </div>
      </div>
    </article>
  )
}
