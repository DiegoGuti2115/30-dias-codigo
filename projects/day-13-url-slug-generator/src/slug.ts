/**
 * Núcleo puro de normalización definido por el contrato v1.
 *
 * No interpreta argumentos de proceso ni realiza operaciones de entrada/salida.
 */

export const SLUG_PATTERN = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;

export type SlugErrorCode = 'E_INPUT_NOT_TEXT' | 'E_INPUT_EMPTY' | 'E_INPUT_NOT_NORMALIZABLE';

/** Error de dominio estable para los rechazos del núcleo de normalización. */
export class SlugNormalizationError extends Error {
  public readonly code: SlugErrorCode;

  public constructor(code: SlugErrorCode) {
    super(code);
    this.name = 'SlugNormalizationError';
    this.code = code;
  }
}

/**
 * Sustituciones latinas mínimas cerradas por el contrato v1.
 * Se aplican tras NFKD y la eliminación de marcas, antes del filtrado ASCII.
 */
const LATIN_REPLACEMENTS: Readonly<Record<string, string>> = {
  ß: 'ss',
  æ: 'ae',
  œ: 'oe',
  ø: 'o',
  ð: 'd',
  þ: 'th',
  ł: 'l',
  đ: 'd',
  ı: 'i',
};

const COMBINING_MARK = /\p{M}/u;
const ASCII_SLUG_CHARACTER = /^[a-z0-9]$/;

/**
 * Convierte una cadena primitiva en un slug ASCII canónico.
 *
 * @throws {SlugNormalizationError} con `E_INPUT_NOT_TEXT` si la entrada no es
 * una cadena primitiva; con `E_INPUT_EMPTY` si está vacía tras el recorte
 * Unicode; o con `E_INPUT_NOT_NORMALIZABLE` si no deja contenido permitido.
 */
export function normalizeSlug(input: unknown): string {
  if (typeof input !== 'string') {
    throw new SlugNormalizationError('E_INPUT_NOT_TEXT');
  }

  const trimmedInput = input.trim();
  if (trimmedInput.length === 0) {
    throw new SlugNormalizationError('E_INPUT_EMPTY');
  }

  const normalizedInput = trimmedInput.normalize('NFKD').toLowerCase();
  const output: string[] = [];
  let hasPendingBoundary = false;

  for (const character of normalizedInput) {
    if (COMBINING_MARK.test(character)) {
      continue;
    }

    const replacement = LATIN_REPLACEMENTS[character];
    const fragment = replacement ?? character;

    for (const fragmentCharacter of fragment) {
      if (ASCII_SLUG_CHARACTER.test(fragmentCharacter)) {
        if (hasPendingBoundary && output.length > 0) {
          output.push('-');
        }

        output.push(fragmentCharacter);
        hasPendingBoundary = false;
      } else {
        hasPendingBoundary = true;
      }
    }
  }

  const slug = output.join('');
  if (slug.length === 0) {
    throw new SlugNormalizationError('E_INPUT_NOT_NORMALIZABLE');
  }

  return slug;
}
