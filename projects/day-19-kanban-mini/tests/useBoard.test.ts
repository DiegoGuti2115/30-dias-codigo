import { createElement } from 'react'
import { act, create, type ReactTestRenderer } from 'react-test-renderer'
import { describe, expect, it } from 'vitest'
import { useBoard, type UseBoardResult } from '../src/hooks/useBoard'
import { createMemoryStorage } from './memoryStorage'
import { failingStorage } from './failingStorage'
import { createFailingSaveStorage } from './failingSaveStorage'
import boardFixture from '../data/board.json'
import type { Board, CardDraft } from '../src/utils/types'

;(globalThis as typeof globalThis & { IS_REACT_ACT_ENVIRONMENT: boolean }).IS_REACT_ACT_ENVIRONMENT = true

function renderBoard(options: Parameters<typeof useBoard>[0] = {}): {
  getResult: () => UseBoardResult
  renderer: ReactTestRenderer
} {
  let result!: UseBoardResult

  function TestHarness() {
    result = useBoard(options)
    return null
  }

  let renderer!: ReactTestRenderer
  act(() => {
    renderer = create(createElement(TestHarness))
  })

  return { getResult: () => result, renderer }
}

const newCard: CardDraft = {
  title: 'Nueva tarea',
  description: 'Descripción de prueba',
}

describe('useBoard', () => {
  it('hydrates a cloned fixture with cards in all columns', async () => {
    const { getResult, renderer } = renderBoard({ storage: createMemoryStorage() })
    await act(async () => {})
    const result = getResult()

    expect(result.board.title).toBe('Reto de 30 días')
    expect(result.board.cards.map((card) => card.id)).toEqual([
      'card-001',
      'card-002',
      'card-003',
      'card-004',
    ])
    expect(new Set(result.board.cards.map((card) => card.columnId))).toEqual(
      new Set(['todo', 'in-progress', 'done']),
    )
    renderer.unmount()
  })

  it('creates, updates, moves and deletes through local actions', async () => {
    const { getResult, renderer } = renderBoard({
      createId: () => 'card-created',
      now: () => '2026-09-17T10:00:00.000Z',
      storage: createMemoryStorage(),
    })
    await act(async () => {})

    act(() => getResult().actions.addCard(newCard))
    expect(getResult().board.cards.find((card) => card.id === 'card-created')).toMatchObject({
      title: 'Nueva tarea',
      columnId: 'todo',
      position: 2,
    })

    act(() => getResult().actions.updateCard('card-created', {
      title: 'Tarea actualizada',
      description: 'Descripción actualizada',
    }))
    expect(getResult().board.cards.find((card) => card.id === 'card-created')).toMatchObject({
      title: 'Tarea actualizada',
      description: 'Descripción actualizada',
    })

    act(() => getResult().actions.moveCard('card-created', 'done'))
    expect(getResult().board.cards.find((card) => card.id === 'card-created')?.columnId).toBe('done')

    act(() => getResult().actions.requestDelete('card-created'))
    expect(getResult().pendingDeletion).toBe('card-created')
    act(() => getResult().actions.confirmDelete())
    expect(getResult().board.cards.some((card) => card.id === 'card-created')).toBe(false)
    expect(getResult().pendingDeletion).toBeNull()
    expect(getResult().error).toBeNull()
    renderer.unmount()
  })

  it('keeps the board unchanged and exposes validation errors', async () => {
    const { getResult, renderer } = renderBoard({
      createId: () => 'card-invalid',
      now: () => '2026-09-17T10:00:00.000Z',
      storage: createMemoryStorage(),
    })
    await act(async () => {})
    const originalCards = getResult().board.cards

    act(() => getResult().actions.addCard({ title: '  ', description: '' }))

    expect(getResult().board.cards).toEqual(originalCards)
    expect(getResult().error).toBe('El título es obligatorio.')

    act(() => getResult().actions.clearError())
    expect(getResult().error).toBeNull()
    renderer.unmount()
  })

  it('can cancel a pending deletion without changing the board', async () => {
    const { getResult, renderer } = renderBoard({ storage: createMemoryStorage() })
    await act(async () => {})
    const originalCards = getResult().board.cards

    act(() => getResult().actions.requestDelete('card-001'))
    act(() => getResult().actions.cancelDelete())

    expect(getResult().pendingDeletion).toBeNull()
    expect(getResult().board.cards).toEqual(originalCards)
    renderer.unmount()
  })

  it('rehydrates a persisted board supplied by the storage adapter', async () => {
    const sourceBoard = boardFixture as Board
    const storedBoard: Board = {
      ...sourceBoard,
      cards: [sourceBoard.cards[3]],
    }
    const { getResult, renderer } = renderBoard({ storage: createMemoryStorage(storedBoard) })

    await act(async () => {})

    expect(getResult().board.cards.map((card) => card.id)).toEqual(['card-004'])
    expect(getResult().storageMode).toBe('indexeddb')
    renderer.unmount()
  })

  it('keeps the board usable in memory when storage loading fails', async () => {
    const { getResult, renderer } = renderBoard({
      storage: failingStorage,
      createId: () => 'memory-card',
      now: () => '2026-09-17T10:00:00.000Z',
    })

    await act(async () => {})

    expect(getResult().storageMode).toBe('memory')
    expect(getResult().storageNotice).toContain('IndexedDB')
    act(() => getResult().actions.addCard(newCard))
    expect(getResult().board.cards.some((card) => card.id === 'memory-card')).toBe(true)
    renderer.unmount()
  })

  it('switches to memory mode when a persistence write fails', async () => {
    const sourceBoard = boardFixture as Board
    const { getResult, renderer } = renderBoard({
      storage: createFailingSaveStorage(sourceBoard),
      createId: () => 'write-failure-card',
      now: () => '2026-09-17T10:00:00.000Z',
    })

    await act(async () => {})
    act(() => getResult().actions.addCard(newCard))
    await act(async () => {})

    expect(getResult().board.cards.some((card) => card.id === 'write-failure-card')).toBe(true)
    expect(getResult().storageMode).toBe('memory')
    expect(getResult().storageNotice).toContain('IndexedDB')
    renderer.unmount()
  })
})
