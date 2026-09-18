import { getCardsInColumn } from '../utils/kanbanRules'
import type { Board, Card, Column, ColumnId } from '../utils/types'
import { TaskCard } from './TaskCard'

interface BoardColumnProps {
  board: Board
  column: Column
  onAdd: (columnId: ColumnId) => void
  onEdit: (card: Card) => void
  onDelete: (cardId: string) => void
  onMove: (cardId: string, columnId: ColumnId) => void
}

const columnMarkers: Record<ColumnId, string> = {
  todo: '01',
  'in-progress': '02',
  done: '03',
}

export function BoardColumn({ board, column, onAdd, onEdit, onDelete, onMove }: BoardColumnProps) {
  const cards = getCardsInColumn(board, column.id)

  return (
    <section className={`board-column board-column-${column.id}`} aria-labelledby={`${column.id}-heading`}>
      <header className="column-header">
        <div className="column-title-wrap">
          <span className="column-marker">{columnMarkers[column.id]}</span>
          <div>
            <h2 id={`${column.id}-heading`}>{column.title}</h2>
            <span className="column-count">{cards.length} {cards.length === 1 ? 'tarea' : 'tareas'}</span>
          </div>
        </div>
        <button className="add-button" type="button" onClick={() => onAdd(column.id)} aria-label={`Añadir tarea a ${column.title}`}>
          <span aria-hidden="true">+</span>
        </button>
      </header>
      <div className="column-cards">
        {cards.length > 0 ? cards.map((card) => (
          <TaskCard key={card.id} card={card} columns={board.columns} onEdit={onEdit} onDelete={onDelete} onMove={onMove} />
        )) : (
          <div className="empty-column">
            <span className="empty-mark" aria-hidden="true">—</span>
            <p>Esta columna está despejada.</p>
            <button className="text-button" type="button" onClick={() => onAdd(column.id)}>Añadir una tarea</button>
          </div>
        )}
      </div>
    </section>
  )
}
