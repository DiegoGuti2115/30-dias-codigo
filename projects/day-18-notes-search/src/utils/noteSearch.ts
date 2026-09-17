import { normalizeTag, normalizeText } from './noteRules'
import type { Note, NoteQuery, NoteSortField, SortDirection } from './types'

function getSearchTokens(text: string): string[] {
  return normalizeText(text).split(' ').filter(Boolean)
}

function getSearchableText(note: Note): string {
  return normalizeText([note.title, note.content, ...note.tags].join(' '))
}

function matchesText(note: Note, text: string): boolean {
  return getSearchTokens(text).every((token) => getSearchableText(note).includes(token))
}

function matchesTag(note: Note, tag: string | null): boolean {
  if (!tag) {
    return true
  }

  const normalizedTag = normalizeTag(tag)
  return normalizedTag.length > 0 && note.tags.some((noteTag) => normalizeTag(noteTag) === normalizedTag)
}

function compareValues(left: string, right: string, field: NoteSortField): number {
  if (field === 'title') {
    return left.localeCompare(right, 'es', { sensitivity: 'base' })
  }

  const leftTime = Date.parse(left)
  const rightTime = Date.parse(right)

  if (Number.isNaN(leftTime) || Number.isNaN(rightTime)) {
    return left.localeCompare(right)
  }

  return leftTime - rightTime
}

function compareNotes(left: Note, right: Note, field: NoteSortField, direction: SortDirection): number {
  const leftValue = field === 'title' ? left.title : left[field]
  const rightValue = field === 'title' ? right.title : right[field]
  const comparison = compareValues(leftValue, rightValue, field)

  if (comparison !== 0) {
    return direction === 'asc' ? comparison : -comparison
  }

  return left.id.localeCompare(right.id)
}

export function searchNotes(notes: Note[], query: NoteQuery): Note[] {
  return notes
    .filter((note) => matchesText(note, query.text) && matchesTag(note, query.tag))
    .sort((left, right) => compareNotes(left, right, query.sortBy, query.sortDirection))
}