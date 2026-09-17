import { describe, expect, it } from 'vitest'
import { extractTags, normalizeTags, normalizeText, validateNoteDraft } from '../src/utils/noteRules'

describe('note rules', () => {
  it('normalizes case, Unicode compatibility and whitespace for comparisons', () => {
    expect(normalizeText('  Café   DE   diseño  ')).toBe('café de diseño')
    expect(normalizeText('ＡＰＩ')).toBe('api')
  })

  it('extracts normalized unique hashtags', () => {
    expect(extractTags('Ideas #React y #react para #Diseño_UX')).toEqual(['react', 'diseño_ux'])
  })

  it('normalizes explicit tags and removes empty or duplicate values', () => {
    expect(normalizeTags([' #Producto ', 'producto', '', '#UX'])).toEqual(['producto', 'ux'])
  })

  it('requires a non-empty title but allows empty content', () => {
    expect(validateNoteDraft({ title: '  ', content: '', tags: [] })).toEqual([
      'El título es obligatorio.',
    ])
    expect(validateNoteDraft({ title: 'Nota rápida', content: '', tags: [] })).toEqual([])
  })
})