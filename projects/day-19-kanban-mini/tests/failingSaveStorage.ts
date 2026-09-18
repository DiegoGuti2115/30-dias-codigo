import type { BoardStorage } from '../src/db/storage'
import type { Board } from '../src/utils/types'

export function createFailingSaveStorage(board: Board): BoardStorage {
  return {
    async load() {
      return board
    },
    async save() {
      throw new Error('Storage write unavailable')
    },
  }
}