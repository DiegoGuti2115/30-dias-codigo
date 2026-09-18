import type { Board as BoardModel, Card, ColumnId } from '../utils/types'
import { BoardColumn } from './BoardColumn'

interface BoardProps {
  board: BoardModel
  onAdd: (columnId: ColumnId) => void
  onEdit: (card: Card) => void
  onDelete: (cardId: string) => void
  onMove: (cardId: string, columnId: ColumnId) => void
}

export function Board({ board, onAdd, onEdit, onDelete, onMove }: BoardProps) {
  return (
    <div className="board-grid">
      {board.columns.map((column) => (
        <BoardColumn key={column.id} board={board} column={column} onAdd={onAdd} onEdit={onEdit} onDelete={onDelete} onMove={onMove} />
      ))}
    </div>
  )
}
