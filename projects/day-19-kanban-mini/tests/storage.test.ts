import 'fake-indexeddb/auto'
import { beforeEach, describe, expect, it } from 'vitest'
import boardFixture from '../data/board.json'
import { indexedDbStorage, resetStorageForTests } from '../src/db/storage'
import type { Board } from '../src/utils/types'

const board = boardFixture as Board

async function clearDatabase(): Promise<void> {
  await resetStorageForTests()
  await new Promise<void>((resolve, reject) => {
    const request = indexedDB.deleteDatabase('kanban-mini')
    request.onsuccess = () => resolve()
    request.onerror = () => reject(request.error)
  })
  await resetStorageForTests()
}

beforeEach(clearDatabase)

describe('indexedDbStorage', () => {
  it('returns null when the board store is empty', async () => {
    expect(await indexedDbStorage.load()).toBeNull()
  })

  it('saves and reloads a complete board snapshot', async () => {
    await indexedDbStorage.save(board)
    await resetStorageForTests()
    const loaded = await indexedDbStorage.load()

    expect(loaded).toEqual(board)
    expect(loaded).not.toBe(board)
    expect(loaded?.cards).not.toBe(board.cards)
  })

  it('does not expose stored references to callers', async () => {
    await indexedDbStorage.save(board)
    const loaded = await indexedDbStorage.load()

    loaded!.cards[0].title = 'Cambio solo en memoria'
    const reloaded = await indexedDbStorage.load()

    expect(reloaded?.cards[0].title).toBe(board.cards[0].title)
  })
})
