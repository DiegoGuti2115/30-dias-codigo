import { useCallback, useEffect, useState } from 'react'
import { createNote, deleteNote, loadNotes, updateNote } from '../db/storage'
import { createMemoryFallback } from './notesFallback'
import type { Note } from '../utils/types'

export type NotesPersistence = 'loading' | 'indexeddb' | 'memory'

type UseNotesResult = {
  notes: Note[]
  persistence: NotesPersistence
  error: string | null
  addNote: (note: Note) => Promise<void>
  editNote: (note: Note) => Promise<void>
  removeNote: (noteId: string) => Promise<void>
}

export function useNotes(seedNotes: Note[]): UseNotesResult {
  const [notes, setNotes] = useState<Note[]>([])
  const [persistence, setPersistence] = useState<NotesPersistence>('loading')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    loadNotes(seedNotes)
      .then((storedNotes) => {
        if (!active) {
          return
        }
        setNotes(storedNotes)
        setPersistence('indexeddb')
        setError(null)
      })
      .catch(() => {
        if (!active) {
          return
        }
        setNotes(createMemoryFallback(seedNotes))
        setPersistence('memory')
        setError('IndexedDB no está disponible. Los cambios vivirán en memoria durante esta sesión.')
      })

    return () => {
      active = false
    }
  }, [seedNotes])

  const addNote = useCallback(async (note: Note) => {
    setNotes((currentNotes) => [note, ...currentNotes])
    try {
      await createNote(note)
    } catch {
      setPersistence('memory')
      setError('No se pudo guardar en IndexedDB. El cambio se conserva en memoria.')
    }
  }, [])

  const editNote = useCallback(async (note: Note) => {
    setNotes((currentNotes) => currentNotes.map((currentNote) => (
      currentNote.id === note.id ? note : currentNote
    )))
    try {
      await updateNote(note)
    } catch {
      setPersistence('memory')
      setError('No se pudo guardar en IndexedDB. El cambio se conserva en memoria.')
    }
  }, [])

  const removeNote = useCallback(async (noteId: string) => {
    setNotes((currentNotes) => currentNotes.filter((note) => note.id !== noteId))
    try {
      await deleteNote(noteId)
    } catch {
      setPersistence('memory')
      setError('No se pudo sincronizar la eliminación. La nota se quitó de esta sesión.')
    }
  }, [])

  return { notes, persistence, error, addNote, editNote, removeNote }
}