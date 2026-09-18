import { useEffect, useReducer } from 'react'
import boardFixture from '../../data/board.json'
import { indexedDbStorage, type BoardStorage, type StorageMode } from '../db/storage'
import { addCard, deleteCard as removeCard, moveCard, updateCard } from '../utils/kanbanRules'
import type { Board, CardDraft, CardId, ColumnId } from '../utils/types'

export interface UseBoardOptions {
  createId?: () => CardId
  now?: () => string
  storage?: BoardStorage
}

export interface BoardActions {
  addCard: (draft: CardDraft, columnId?: ColumnId) => void
  updateCard: (cardId: CardId, draft: CardDraft) => void
  moveCard: (cardId: CardId, columnId: ColumnId, position?: number) => void
  requestDelete: (cardId: CardId) => void
  confirmDelete: () => void
  cancelDelete: () => void
  clearError: () => void
}

export interface UseBoardResult {
  board: Board
  error: string | null
  pendingDeletion: CardId | null
  storageMode: StorageMode
  storageNotice: string | null
  actions: BoardActions
}

const defaultCreateId = (): CardId => `card-${crypto.randomUUID()}`
const defaultNow = (): string => new Date().toISOString()

interface BoardState {
  board: Board
  error: string | null
  pendingDeletion: CardId | null
  hydrated: boolean
  storageMode: StorageMode
  storageNotice: string | null
}

type BoardStateAction =
  | { type: 'change'; change: (currentBoard: Board) => Board }
  | { type: 'request-delete'; cardId: CardId }
  | { type: 'confirm-delete' }
  | { type: 'cancel-delete' }
  | { type: 'clear-error' }
  | { type: 'hydrate'; board: Board | null }
  | { type: 'storage-failed' }

function cloneBoard(source: Board): Board {
  return {
    ...source,
    columns: source.columns.map((column) => ({ ...column })),
    cards: source.cards.map((card) => ({ ...card })),
  }
}

function boardReducer(state: BoardState, action: BoardStateAction): BoardState {
  if (action.type === 'hydrate') {
    return {
      ...state,
      board: cloneBoard(action.board ?? (boardFixture as Board)),
      hydrated: true,
      storageMode: 'indexeddb',
      storageNotice: null,
    }
  }

  if (action.type === 'storage-failed') {
    return {
      ...state,
      hydrated: true,
      storageMode: 'memory',
      storageNotice: 'IndexedDB no está disponible. Los cambios vivirán solo en esta sesión.',
    }
  }

  if (action.type === 'clear-error') {
    return { ...state, error: null }
  }

  if (action.type === 'request-delete') {
    if (!state.board.cards.some((card) => card.id === action.cardId)) {
      return { ...state, error: `No existe la tarjeta "${action.cardId}".` }
    }

    return { ...state, error: null, pendingDeletion: action.cardId }
  }

  if (action.type === 'cancel-delete') {
    return { ...state, error: null, pendingDeletion: null }
  }

  if (action.type === 'confirm-delete') {
    if (!state.pendingDeletion) {
      return state
    }

    try {
      return {
        board: removeCard(state.board, state.pendingDeletion),
        error: null,
        pendingDeletion: null,
        hydrated: state.hydrated,
        storageMode: state.storageMode,
        storageNotice: state.storageNotice,
      }
    } catch (cause) {
      return {
        ...state,
        error: cause instanceof Error ? cause.message : 'No se pudo eliminar la tarjeta.',
      }
    }
  }

  try {
    return {
      board: action.change(state.board),
      error: null,
      pendingDeletion: null,
      hydrated: state.hydrated,
      storageMode: state.storageMode,
      storageNotice: state.storageNotice,
    }
  } catch (cause) {
    return {
      ...state,
      error: cause instanceof Error ? cause.message : 'No se pudo actualizar el tablero.',
    }
  }
}

export function useBoard(options: UseBoardOptions = {}): UseBoardResult {
  const createId = options.createId ?? defaultCreateId
  const now = options.now ?? defaultNow
  const storage = options.storage ?? indexedDbStorage
  const [state, dispatch] = useReducer(boardReducer, {
    board: boardFixture as Board,
    error: null,
    pendingDeletion: null,
    hydrated: false,
    storageMode: 'loading',
    storageNotice: null,
  }, (initialState) => ({
    board: cloneBoard(initialState.board),
    error: initialState.error,
    pendingDeletion: initialState.pendingDeletion,
    hydrated: initialState.hydrated,
    storageMode: initialState.storageMode as StorageMode,
    storageNotice: initialState.storageNotice,
  }))

  useEffect(() => {
    let active = true

    storage.load()
      .then((storedBoard) => {
        if (active) {
          dispatch({ type: 'hydrate', board: storedBoard })
        }
      })
      .catch(() => {
        if (active) {
          dispatch({ type: 'storage-failed' })
        }
      })

    return () => {
      active = false
    }
  }, [storage])

  useEffect(() => {
    if (!state.hydrated || state.storageMode !== 'indexeddb') {
      return
    }

    storage.save(state.board).catch(() => {
      dispatch({ type: 'storage-failed' })
    })
  }, [state.board, state.hydrated, state.storageMode, storage])

  function applyChange(change: (currentBoard: Board) => Board): void {
    dispatch({ type: 'change', change })
  }

  const actions: BoardActions = {
    addCard: (draft, columnId) => {
      applyChange((currentBoard) => addCard(currentBoard, draft, { id: createId(), now: now(), columnId }))
    },
    updateCard: (cardId, draft) => {
      applyChange((currentBoard) => updateCard(currentBoard, cardId, draft, now()))
    },
    moveCard: (cardId, columnId, position) => {
      applyChange((currentBoard) => moveCard(currentBoard, cardId, columnId, { now: now(), position }))
    },
    requestDelete: (cardId) => dispatch({ type: 'request-delete', cardId }),
    confirmDelete: () => dispatch({ type: 'confirm-delete' }),
    cancelDelete: () => dispatch({ type: 'cancel-delete' }),
    clearError: () => dispatch({ type: 'clear-error' }),
  }

  return {
    board: state.board,
    error: state.error,
    pendingDeletion: state.pendingDeletion,
    storageMode: state.storageMode,
    storageNotice: state.storageNotice,
    actions,
  }
}