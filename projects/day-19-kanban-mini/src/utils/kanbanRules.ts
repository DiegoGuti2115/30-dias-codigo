import { COLUMN_IDS, type Board, type Card, type CardDraft, type CardId, type ColumnId, type CreateCardOptions, type MoveCardOptions } from './types'

export function normalizeText(value: string): string {
  return value.normalize('NFKC').trim().replace(/\s+/gu, ' ')
}

export function validateCardDraft(draft: CardDraft): string[] {
  const errors: string[] = []

  if (!normalizeText(draft.title)) {
    errors.push('El título es obligatorio.')
  }

  return errors
}

export function normalizeCardDraft(draft: CardDraft): CardDraft {
  const errors = validateCardDraft(draft)

  if (errors.length > 0) {
    throw new Error(errors.join(' '))
  }

  return {
    title: normalizeText(draft.title),
    description: normalizeText(draft.description),
  }
}

export function isColumnId(value: string): value is ColumnId {
  return COLUMN_IDS.includes(value as ColumnId)
}

export function getCardsInColumn(board: Board, columnId: ColumnId): Card[] {
  return board.cards
    .filter((card) => card.columnId === columnId)
    .sort((first, second) => first.position - second.position)
}

export function normalizePositions(cards: Card[]): Card[] {
  return COLUMN_IDS.flatMap((columnId) =>
    getCardsInColumn({ id: '', title: '', columns: [], cards }, columnId).map((card, position) => ({
      ...card,
      position,
    })),
  )
}

export function addCard(board: Board, draft: CardDraft, options: CreateCardOptions): Board {
  const normalizedDraft = normalizeCardDraft(draft)

  if (board.cards.some((card) => card.id === options.id)) {
    throw new Error(`Ya existe una tarjeta con el identificador "${options.id}".`)
  }

  const card: Card = {
    ...normalizedDraft,
    id: options.id,
    columnId: options.columnId ?? 'todo',
    position: getCardsInColumn(board, options.columnId ?? 'todo').length,
    createdAt: options.now,
    updatedAt: options.now,
  }

  return {
    ...board,
    cards: normalizePositions([...board.cards, card]),
  }
}

export function updateCard(board: Board, cardId: CardId, draft: CardDraft, now: string): Board {
  const normalizedDraft = normalizeCardDraft(draft)
  let found = false
  const cards = board.cards.map((card) => {
    if (card.id !== cardId) {
      return card
    }

    found = true
    return { ...card, ...normalizedDraft, updatedAt: now }
  })

  if (!found) {
    throw new Error(`No existe la tarjeta "${cardId}".`)
  }

  return { ...board, cards }
}

export function moveCard(board: Board, cardId: CardId, targetColumnId: ColumnId, options: MoveCardOptions): Board {
  const card = board.cards.find((candidate) => candidate.id === cardId)

  if (!card) {
    throw new Error(`No existe la tarjeta "${cardId}".`)
  }

  const remainingCards = board.cards.filter((candidate) => candidate.id !== cardId)
  const targetCards = getCardsInColumn({ ...board, cards: remainingCards }, targetColumnId)
  const requestedPosition = options.position ?? targetCards.length
  const position = Math.max(0, Math.min(requestedPosition, targetCards.length))
  const movedCard: Card = {
    ...card,
    columnId: targetColumnId,
    position,
    updatedAt: options.now,
  }
  const orderedTargetCards = [...targetCards]
  orderedTargetCards.splice(position, 0, movedCard)
  const targetCardIds = new Set(orderedTargetCards.map((targetCard) => targetCard.id))
  const cards = [
    ...remainingCards.filter((remainingCard) => !targetCardIds.has(remainingCard.id)),
    ...orderedTargetCards,
  ]

  return { ...board, cards: normalizePositions(cards) }
}

export function deleteCard(board: Board, cardId: CardId): Board {
  if (!board.cards.some((card) => card.id === cardId)) {
    throw new Error(`No existe la tarjeta "${cardId}".`)
  }

  return {
    ...board,
    cards: normalizePositions(board.cards.filter((card) => card.id !== cardId)),
  }
}
