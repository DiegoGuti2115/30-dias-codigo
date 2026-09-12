import assert from 'node:assert/strict';
import test from 'node:test';

import { normalizeSlug, SLUG_PATTERN, SlugNormalizationError } from '../dist/slug.js';

const normalizationCases = [
  ['Hola Mundo', 'hola-mundo'],
  ['  Guía rápida de TypeScript  ', 'guia-rapida-de-typescript'],
  ['Café, té y azúcar', 'cafe-te-y-azucar'],
  ['À bientôt', 'a-bientot'],
  ['Crème brûlée', 'creme-brulee'],
  ['niño', 'nino'],
  ['áéíóúüñç', 'aeiouunc'],
  ['API_v2: novedades', 'api-v2-novedades'],
  ['Rock & Roll!!!', 'rock-roll'],
  ['Málaga—Sevilla / 2026', 'malaga-sevilla-2026'],
  ['c++ guía', 'c-guia'],
  ['uno___---///dos', 'uno-dos'],
  ['--Hola--', 'hola'],
  ['a\tb\nc', 'a-b-c'],
  ['uno\u00a0dos', 'uno-dos'],
  ['Precio € 10', 'precio-10'],
  ['uno中文dos', 'uno-dos'],
  ['привет mundo', 'mundo'],
  ['hola 😀 mundo', 'hola-mundo'],
  ['Straße & Æsir', 'strasse-aesir'],
  ['Œuvre', 'oeuvre'],
  ['Øresund', 'oresund'],
  ['Ðagur Þór', 'dagur-thor'],
  ['Łódź Đuro', 'lodz-duro'],
  ['İstanbul ıslak', 'istanbul-islak'],
  ['Cafe\u0301 y A\u0308rbol', 'cafe-y-arbol'],
  ['Versión 2026 v2', 'version-2026-v2'],
  ['---uno...dos___tres---', 'uno-dos-tres'],
];

for (const [input, expected] of normalizationCases) {
  test(`normaliza ${JSON.stringify(input)}`, () => {
    assert.equal(normalizeSlug(input), expected);
  });
}

test('cada resultado válido es canónico, idempotente y determinista', () => {
  for (const [input, expected] of normalizationCases) {
    const slug = normalizeSlug(input);

    assert.equal(slug, expected);
    assert.match(slug, SLUG_PATTERN);
    assert.doesNotMatch(slug, /--/);
    assert.equal(slug.startsWith('-'), false);
    assert.equal(slug.endsWith('-'), false);
    assert.equal(normalizeSlug(input), slug);
    assert.equal(normalizeSlug(slug), slug);
  }
});

const invalidCases = [
  ['', 'E_INPUT_EMPTY'],
  ['   ', 'E_INPUT_EMPTY'],
  ['\u00a0', 'E_INPUT_EMPTY'],
  ['---', 'E_INPUT_NOT_NORMALIZABLE'],
  ['!!!', 'E_INPUT_NOT_NORMALIZABLE'],
  ['中文', 'E_INPUT_NOT_NORMALIZABLE'],
  ['😀---💡', 'E_INPUT_NOT_NORMALIZABLE'],
  [undefined, 'E_INPUT_NOT_TEXT'],
  [null, 'E_INPUT_NOT_TEXT'],
  [42, 'E_INPUT_NOT_TEXT'],
  [false, 'E_INPUT_NOT_TEXT'],
  [new String('texto'), 'E_INPUT_NOT_TEXT'],
  [{}, 'E_INPUT_NOT_TEXT'],
];

for (const [input, expectedCode] of invalidCases) {
  test(`rechaza ${String(input)} con ${expectedCode}`, () => {
    assert.throws(
      () => normalizeSlug(input),
      (error) =>
        error instanceof SlugNormalizationError &&
        error.code === expectedCode &&
        error.message === expectedCode,
    );
  });
}

test('no gestiona colisiones ni añade sufijos implícitos', () => {
  assert.equal(normalizeSlug('Café'), 'cafe');
  assert.equal(normalizeSlug('Cafe'), 'cafe');
  assert.equal(normalizeSlug('A/B'), 'a-b');
  assert.equal(normalizeSlug('A B'), 'a-b');
});
