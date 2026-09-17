import { describe, expect, it } from 'vitest'
import { searchNotes } from '../src/utils/noteSearch'
import type { Note, NoteQuery } from '../src/utils/types'

const notes: Note[] = [
  {
    id: 'note-b',
    title: 'Diseño del buscador',
    content: 'Definir una experiencia rápida para encontrar información.',
    tags: ['Frontend', 'UX'],
    createdAt: '2026-09-10T10:00:00.000Z',
    updatedAt: '2026-09-12T10:00:00.000Z',
  },
  {
    id: 'note-a',
    title: 'Plan de pruebas',
    content: 'Cubrir búsquedas y filtros del buscador.',
    tags: ['calidad', 'frontend'],
    createdAt: '2026-09-11T10:00:00.000Z',
    updatedAt: '2026-09-12T10:00:00.000Z',
  },
  {
    id: 'note-c',
    title: 'Reunión de producto',
    content: 'Revisar prioridades del siguiente ciclo.',
    tags: ['producto'],
    createdAt: '2026-09-09T10:00:00.000Z',
    updatedAt: '2026-09-13T10:00:00.000Z',
  },
]

const defaultQuery: NoteQuery = {
  text: '',
  tag: null,
  sortBy: 'updatedAt',
  sortDirection: 'desc',
}

describe('searchNotes', () => {
  it('returns all notes for an empty query in the requested order', () => {
    const result = searchNotes(notes, defaultQuery)

    expect(result.map((note) => note.id)).toEqual(['note-c', 'note-a', 'note-b'])
  })

  it('matches every search term across title, content and tags', () => {
    const result = searchNotes(notes, { ...defaultQuery, text: '  BUSCADOR   frontend ' })

    expect(result.map((note) => note.id)).toEqual(['note-a', 'note-b'])
  })

  it('applies an exact, case-insensitive tag filter', () => {
    const result = searchNotes(notes, { ...defaultQuery, tag: '#FRONTEND' })

    expect(result.map((note) => note.id)).toEqual(['note-a', 'note-b'])
  })

  it('combines text search and tag filtering', () => {
    const result = searchNotes(notes, { ...defaultQuery, text: 'experiencia rápida', tag: 'frontend' })

    expect(result.map((note) => note.id)).toEqual(['note-b'])
  })

  it('supports ascending title order and leaves the source array unchanged', () => {
    const originalIds = notes.map((note) => note.id)
    const result = searchNotes(notes, { ...defaultQuery, sortBy: 'title', sortDirection: 'asc' })

    expect(result.map((note) => note.id)).toEqual(['note-b', 'note-a', 'note-c'])
    expect(notes.map((note) => note.id)).toEqual(originalIds)
  })

  it('returns no notes for a query without matches', () => {
    expect(searchNotes(notes, { ...defaultQuery, text: 'inexistente' })).toEqual([])
  })
})