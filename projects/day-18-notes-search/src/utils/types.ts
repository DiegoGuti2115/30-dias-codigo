export type NoteId = string

export interface Note {
  id: NoteId
  title: string
  content: string
  tags: string[]
  createdAt: string
  updatedAt: string
}

export type NoteDraft = Pick<Note, 'title' | 'content' | 'tags'>

export type NoteSortField = 'updatedAt' | 'createdAt' | 'title'

export type SortDirection = 'asc' | 'desc'

export interface NoteQuery {
  text: string
  tag: string | null
  sortBy: NoteSortField
  sortDirection: SortDirection
}