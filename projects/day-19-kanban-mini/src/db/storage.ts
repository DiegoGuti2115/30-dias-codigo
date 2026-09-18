import { openDB, type DBSchema, type IDBPDatabase } from 'idb'
import type { Board } from '../utils/types'

const DATABASE_NAME = 'kanban-mini'
const DATABASE_VERSION = 1
const BOARD_STORE = 'boards'
const BOARD_KEY = 'main'

interface KanbanDatabase extends DBSchema {
  boards: {
    key: string
    value: Board
  }
}

export type StorageMode = 'loading' | 'indexeddb' | 'memory'

export interface BoardStorage {
  load: () => Promise<Board | null>
  save: (board: Board) => Promise<void>
}

function cloneBoard(board: Board): Board {
  return {
    ...board,
    columns: board.columns.map((column) => ({ ...column })),
    cards: board.cards.map((card) => ({ ...card })),
  }
}

let databasePromise: Promise<IDBPDatabase<KanbanDatabase>> | null = null

function getDatabase(): Promise<IDBPDatabase<KanbanDatabase>> {
  if (typeof indexedDB === 'undefined') {
    return Promise.reject(new Error('IndexedDB no está disponible en este navegador.'))
  }

  databasePromise ??= openDB<KanbanDatabase>(DATABASE_NAME, DATABASE_VERSION, {
    upgrade(database) {
      if (!database.objectStoreNames.contains(BOARD_STORE)) {
        database.createObjectStore(BOARD_STORE)
      }
    },
  })

  return databasePromise
}

export const indexedDbStorage: BoardStorage = {
  async load() {
    const database = await getDatabase()
    const board = await database.get(BOARD_STORE, BOARD_KEY)
    return board ? cloneBoard(board) : null
  },
  async save(board) {
    const database = await getDatabase()
    await database.put(BOARD_STORE, cloneBoard(board), BOARD_KEY)
  },
}

export async function resetStorageForTests(): Promise<void> {
  if (databasePromise) {
    const database = await databasePromise.catch(() => null)
    database?.close()
  }

  databasePromise = null
}
