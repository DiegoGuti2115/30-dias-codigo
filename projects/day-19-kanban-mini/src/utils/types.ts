export const COLUMN_IDS = ['todo', 'in-progress', 'done'] as const

export type ColumnId = (typeof COLUMN_IDS)[number]
export type CardId = string

export interface Column {
  id: ColumnId
  title: string
}

export interface Card {
  id: CardId
  title: string
  description: string
  columnId: ColumnId
  position: number
  createdAt: string
  updatedAt: string
}

export interface Board {
  id: string
  title: string
  columns: Column[]
  cards: Card[]
}

export type CardDraft = Pick<Card, 'title' | 'description'>

export interface CreateCardOptions {
  id: CardId
  now: string
  columnId?: ColumnId
}

export interface MoveCardOptions {
  now: string
  position?: number
}

export type BoardAction =
  | { type: 'card-added'; card: Card }
  | { type: 'card-updated'; card: Card }
  | { type: 'card-moved'; cardId: CardId; columnId: ColumnId; position?: number }
  | { type: 'card-deleted'; cardId: CardId }
