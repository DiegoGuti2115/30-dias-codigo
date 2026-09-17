import type { Note } from '../utils/types'

export function createMemoryFallback(notes: Note[]): Note[] {
  return [...notes]
}