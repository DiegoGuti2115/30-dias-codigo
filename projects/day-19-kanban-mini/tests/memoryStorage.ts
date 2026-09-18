import type { Board } from '../src/utils/types'
import type { BoardStorage } from '../src/db/storage'

export function createMemoryStorage(initialBoard: Board | null = null): BoardStorage {
  let storedBoard = initialBoard

  return {
    async load() {
      return storedBoard
    },
    async save(board) {
      storedBoard = board
    },
  }
}
