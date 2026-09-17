import type { NoteDraft } from './types'

export function normalizeText(value: string): string {
  return value.normalize('NFKC').trim().replace(/\s+/gu, ' ').toLocaleLowerCase('es')
}

export function normalizeTag(value: string): string {
  return normalizeText(value.trim().replace(/^#/u, ''))
}

export function normalizeTags(tags: string[]): string[] {
  return [...new Set(tags.map(normalizeTag).filter(Boolean))]
}

export function extractTags(text: string): string[] {
  const matches = text.matchAll(/#([\p{L}\p{N}_-]+)/gu)
  return normalizeTags([...matches].map((match) => match[1]))
}

export function validateNoteDraft(draft: NoteDraft): string[] {
  const errors: string[] = []

  if (!draft.title.trim()) {
    errors.push('El título es obligatorio.')
  }

  return errors
}