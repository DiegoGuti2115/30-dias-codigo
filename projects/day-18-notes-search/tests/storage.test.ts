import 'fake-indexeddb/auto'
import { deleteDB } from 'idb'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { closeNotesDatabase, createNote, deleteNote, loadNotes, NOTES_DATABASE_NAME, updateNote } from '../src/db/storage'
import { createMemoryFallback } from '../src/hooks/notesFallback'
import type { Note } from '../src/utils/types'

const seedNote: Note = {
  id: 'seed-note',
  title: 'Nota inicial',
  content: 'Contenido inicial',
  tags: ['demo'],
  createdAt: '2026-09-16T08:00:00.000Z',
  updatedAt: '2026-09-16T08:00:00.000Z',
}

beforeEach(async () => {
  closeNotesDatabase()
  await deleteDB(NOTES_DATABASE_NAME)
})

describe('notes storage', () => {
  it('seeds an empty database once and reuses stored notes', async () => {
    const firstLoad = await loadNotes([seedNote])
    const secondLoad = await loadNotes([{ ...seedNote, title: 'Fixture diferente' }])

    expect(firstLoad).toEqual([seedNote])
    expect(secondLoad).toEqual([seedNote])
  })

  it('persists create, update and delete operations after reopening', async () => {
    const createdNote = { ...seedNote, id: 'created-note', title: 'Nota creada' }
    await loadNotes([seedNote])
    await createNote(createdNote)
    await updateNote({ ...createdNote, title: 'Nota actualizada' })
    closeNotesDatabase()

    const reopenedNotes = await loadNotes([])
    expect(reopenedNotes).toContainEqual({ ...createdNote, title: 'Nota actualizada' })

    await deleteNote(createdNote.id)
    const notesAfterDelete = await loadNotes([])
    expect(notesAfterDelete).toContainEqual(seedNote)
    expect(notesAfterDelete).not.toContainEqual({ ...createdNote, title: 'Nota actualizada' })
  })

  it('creates an independent memory snapshot for the fallback', () => {
    const sourceNotes = [seedNote]
    const fallbackNotes = createMemoryFallback(sourceNotes)

    expect(fallbackNotes).toEqual(sourceNotes)
    expect(fallbackNotes).not.toBe(sourceNotes)
  })

  it('rejects cleanly when IndexedDB is unavailable', async () => {
    vi.stubGlobal('indexedDB', undefined)

    await expect(loadNotes([])).rejects.toThrow('IndexedDB no está disponible')

    vi.unstubAllGlobals()
  })
})