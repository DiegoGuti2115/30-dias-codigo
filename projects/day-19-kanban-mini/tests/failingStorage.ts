import type { BoardStorage } from '../src/db/storage'

export const failingStorage: BoardStorage = {
  async load() {
    throw new Error('Storage unavailable')
  },
  async save() {
    throw new Error('Storage unavailable')
  },
}
