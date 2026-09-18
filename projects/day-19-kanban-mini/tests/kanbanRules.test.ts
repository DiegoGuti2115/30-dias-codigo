import { describe, expect, it } from 'vitest'
import boardFixture from '../data/board.json'
import {
  addCard,
  deleteCard,
  getCardsInColumn,
  isColumnId,
  moveCard,
  normalizeCardDraft,
  normalizePositions,
  updateCard,
  validateCardDraft,
} from '../src/utils/kanbanRules'
import type { Board, Card } from '../src/utils/types'

const board = boardFixture as Board

function cardIds(currentBoard: Board, columnId: 'todo' | 'in-progress' | 'done'): string[] {
  return getCardsInColumn(currentBoard, columnId).map((card) => card.id)
}

describe('kanban model', () => {
  it('defines only the three MVP columns', () => {
    expect(isColumnId('todo')).toBe(true)
    expect(isColumnId('in-progress')).toBe(true)
    expect(isColumnId('done')).toBe(true)
    expect(isColumnId('blocked')).toBe(false)
  })

  it('validates a required title and normalizes draft text', () => {
    expect(validateCardDraft({ title: '  ', description: '' })).toEqual(['El título es obligatorio.'])
    expect(normalizeCardDraft({ title: '  Preparar   demo  ', description: '  Flujo   principal ' })).toEqual({
      title: 'Preparar demo',
      description: 'Flujo principal',
    })
  })

  it('adds a card to todo without mutating the source board', () => {
    const result = addCard(board, { title: '  Nueva tarjeta ', description: '' }, {
      id: 'card-new',
      now: '2026-09-17T10:00:00.000Z',
    })

    expect(cardIds(result, 'todo')).toEqual(['card-001', 'card-002', 'card-new'])
    expect(result.cards.find((card) => card.id === 'card-new')).toMatchObject({
      title: 'Nueva tarjeta',
      columnId: 'todo',
      position: 2,
    })
    expect(board.cards).toHaveLength(4)
  })

  it('rejects duplicate identifiers and missing cards', () => {
    expect(() => addCard(board, { title: 'Duplicada', description: '' }, {
      id: 'card-001',
      now: '2026-09-17T10:00:00.000Z',
    })).toThrow('Ya existe una tarjeta')
    expect(() => updateCard(board, 'missing', { title: 'Nueva', description: '' }, '2026-09-17T10:00:00.000Z'))
      .toThrow('No existe la tarjeta')
  })

  it('updates a card while preserving identity and timestamps', () => {
    const result = updateCard(board, 'card-001', {
      title: '  Modelo validado ',
      description: ' Reglas cerradas ',
    }, '2026-09-17T10:00:00.000Z')
    const updated = result.cards.find((card) => card.id === 'card-001')

    expect(updated).toMatchObject({
      id: 'card-001',
      title: 'Modelo validado',
      description: 'Reglas cerradas',
      createdAt: '2026-09-17T08:00:00.000Z',
      updatedAt: '2026-09-17T10:00:00.000Z',
    })
    expect(board.cards[0].title).toBe('Definir el modelo del tablero')
  })

  it('moves a card to an explicit position and compacts both columns', () => {
    const result = moveCard(board, 'card-003', 'todo', {
      now: '2026-09-17T10:00:00.000Z',
      position: 1,
    })

    expect(cardIds(result, 'todo')).toEqual(['card-001', 'card-003', 'card-002'])
    expect(cardIds(result, 'in-progress')).toEqual([])
    expect(getCardsInColumn(result, 'todo').map((card) => card.position)).toEqual([0, 1, 2])
    expect(board.cards.find((card) => card.id === 'card-003')?.columnId).toBe('in-progress')
  })

  it('clamps positions and keeps an empty column valid', () => {
    const afterMoving = moveCard(board, 'card-004', 'in-progress', {
      now: '2026-09-17T10:00:00.000Z',
      position: 99,
    })
    const afterDeleting = deleteCard(afterMoving, 'card-003')

    expect(cardIds(afterDeleting, 'done')).toEqual([])
    expect(cardIds(afterDeleting, 'in-progress')).toEqual(['card-004'])
    expect(getCardsInColumn(afterDeleting, 'in-progress')[0].position).toBe(0)
  })

  it('allows an empty description when updating a card', () => {
    const result = updateCard(board, 'card-001', { title: 'Título válido', description: '' }, '2026-09-17T10:00:00.000Z')

    expect(result.cards.find((card) => card.id === 'card-001')).toMatchObject({
      title: 'Título válido',
      description: '',
    })
  })

  it('deletes a card and removes position gaps', () => {
    const result = deleteCard(board, 'card-003')

    expect(cardIds(result, 'in-progress')).toEqual([])
    expect(result.cards).toHaveLength(3)
    expect(result.cards.every((card) => Number.isInteger(card.position))).toBe(true)
  })

  it('normalizes positions independently for every column', () => {
    const cards: Card[] = board.cards.map((card) => ({ ...card, position: 99 }))
    const normalized = normalizePositions(cards)

    expect(normalized.filter((card) => card.columnId === 'todo').map((card) => card.position)).toEqual([0, 1])
    expect(normalized.filter((card) => card.columnId === 'in-progress').map((card) => card.position)).toEqual([0])
    expect(normalized.filter((card) => card.columnId === 'done').map((card) => card.position)).toEqual([0])
  })
})
