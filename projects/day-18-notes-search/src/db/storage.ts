import { openDB, type DBSchema, type IDBPDatabase } from 'idb'
import type { Note } from '../utils/types'

export const NOTES_DATABASE_NAME = 'notes-search'
export const NOTES_STORE_NAME = 'notes'
const NOTES_DATABASE_VERSION = 1

interface NotesDatabase extends DBSchema {
  notes: {
    key: string
    value: Note
    indexes: {
      updatedAt: string
    }
  }
}

let databasePromise: Promise<IDBPDatabase<NotesDatabase>> | undefined

function getDatabase(): Promise<IDBPDatabase<NotesDatabase>> {
  if (typeof indexedDB === 'undefined') {
    return Promise.reject(new Error('IndexedDB no está disponible en este entorno.'))
  }

  databasePromise ??= openDB<NotesDatabase>(NOTES_DATABASE_NAME, NOTES_DATABASE_VERSION, {
    upgrade(database) {
      if (!database.objectStoreNames.contains(NOTES_STORE_NAME)) {
        const store = database.createObjectStore(NOTES_STORE_NAME, { keyPath: 'id' })
        store.createIndex('updatedAt', 'updatedAt')
      }
    },
  })

  return databasePromise
}

export async function loadNotes(seedNotes: Note[]): Promise<Note[]> {
  const database = await getDatabase()
  const transaction = database.transaction(NOTES_STORE_NAME, 'readwrite')
  const storedNotes = await transaction.store.getAll()

  if (storedNotes.length > 0) {
    await transaction.done
    return storedNotes
  }

  for (const note of seedNotes) {
    await transaction.store.put(note)
  }
  await transaction.done
  return [...seedNotes]
}

export async function createNote(note: Note): Promise<Note> {
  const database = await getDatabase()
  await database.put(NOTES_STORE_NAME, note)
  return note
}

export async function updateNote(note: Note): Promise<Note> {
  const database = await getDatabase()
  await database.put(NOTES_STORE_NAME, note)
  return note
}

export async function deleteNote(noteId: string): Promise<void> {
  const database = await getDatabase()
  await database.delete(NOTES_STORE_NAME, noteId)
}

export function closeNotesDatabase(): void {
  databasePromise?.then((database) => database.close()).catch(() => undefined)
  databasePromise = undefined
}