import assert from 'node:assert/strict';
import test from 'node:test';

import { compileSchema } from '../dist/schema.js';
import { validateConfiguration } from '../dist/validator.js';

function plan(overrides = {}) {
  return compileSchema({
    version: 'v1',
    variables: {
      APP_PORT: {
        type: 'number',
        required: true,
        integer: true,
        min: 1,
        max: 65535,
        transforms: ['trim'],
      },
      FEATURE: { type: 'boolean', default: 'TRUE', transforms: ['lowercase'] },
      TAGS: { type: 'list', items: 'string', transforms: ['splitComma'], minItems: 1 },
      API_URL: { type: 'url' },
      API_TOKEN: { type: 'string', secret: true, minLength: 4 },
    },
    ...overrides,
  });
}

test('validates typed values, defaults and safe summaries without exposing values', () => {
  const result = validateConfiguration(
    plan(),
    new Map([
      ['APP_PORT', ' 3000 '],
      ['TAGS', 'one, two'],
      ['API_URL', 'https://example.test/path'],
      ['API_TOKEN', 'secret-value'],
    ]),
  );

  assert.deepEqual(result, {
    valid: true,
    schemaVersion: 'v1',
    summary: { declared: 5, provided: 5, defaulted: 1, warnings: 0 },
    variables: [
      { key: 'API_TOKEN', status: 'valid', source: 'env', secret: true },
      { key: 'API_URL', status: 'valid', source: 'env', secret: false },
      { key: 'APP_PORT', status: 'valid', source: 'env', secret: false },
      { key: 'FEATURE', status: 'valid', source: 'default', secret: false },
      { key: 'TAGS', status: 'valid', source: 'env', secret: false },
    ],
    warnings: [],
  });
  assert.equal(JSON.stringify(result).includes('secret-value'), false);
});

test('distinguishes absent optional variables from present empty values', () => {
  const result = validateConfiguration(
    compileSchema({
      version: 'v1',
      variables: {
        OPTIONAL: { type: 'string', minLength: 1 },
        REQUIRED: { type: 'string', required: true },
      },
    }),
    { OPTIONAL: '', REQUIRED: '' },
  );

  assert.deepEqual(result.error.issues, [
    {
      code: 'E_CONFIG_CONSTRAINT',
      key: 'OPTIONAL',
      rule: 'constraint',
      message: 'El valor no cumple las restricciones declaradas.',
    },
  ]);
});

test('reports conversion and constraint failures ordered by key without exposing values', () => {
  const result = validateConfiguration(plan(), { APP_PORT: '0x10', TAGS: '[1]', API_TOKEN: 'x' });

  assert.deepEqual(result.error.issues, [
    {
      code: 'E_CONFIG_CONSTRAINT',
      key: 'API_TOKEN',
      rule: 'constraint',
      message: 'El valor no cumple las restricciones declaradas.',
    },
    {
      code: 'E_CONFIG_TYPE',
      key: 'APP_PORT',
      rule: 'type',
      message: 'El valor no cumple el tipo declarado.',
    },
  ]);
  assert.equal(JSON.stringify(result).includes('0x10'), false);
});

test('enforces string patterns, enum matching, URL protocols and list JSON limits', () => {
  const compiled = compileSchema({
    version: 'v1',
    variables: {
      CODE: { type: 'string', pattern: { source: '^A+$' } },
      MODE: { type: 'enum', values: ['on'] },
      ENDPOINT: { type: 'url', protocols: ['https:'] },
      FLAGS: { type: 'list', items: 'boolean', maxItems: 1 },
    },
  });
  const result = validateConfiguration(compiled, {
    CODE: 'B',
    MODE: 'off',
    ENDPOINT: 'http://example.test',
    FLAGS: '[true, false]',
  });

  assert.deepEqual(
    result.error.issues.map((entry) => [entry.key, entry.code]),
    [
      ['CODE', 'E_CONFIG_CONSTRAINT'],
      ['ENDPOINT', 'E_CONFIG_CONSTRAINT'],
      ['FLAGS', 'E_CONFIG_CONSTRAINT'],
      ['MODE', 'E_CONFIG_CONSTRAINT'],
    ],
  );
});

test('applies unknown-key policies without revealing unknown values', () => {
  const warningResult = validateConfiguration(plan(), {
    APP_PORT: '1',
    TAGS: 'x',
    LEGACY: 'hidden',
  });
  assert.equal(warningResult.valid, true);
  assert.deepEqual(warningResult.warnings, [
    {
      code: 'W_CONFIG_UNKNOWN_KEY',
      key: 'LEGACY',
      message: 'La clave no está declarada en el esquema.',
    },
  ]);

  const errorResult = validateConfiguration(plan({ unknownKeys: 'error' }), {
    APP_PORT: '1',
    TAGS: 'x',
    LEGACY: 'hidden',
  });
  assert.deepEqual(errorResult.error.issues, [
    {
      code: 'E_CONFIG_UNKNOWN_KEY',
      key: 'LEGACY',
      rule: 'unknownKey',
      message: 'La clave no está declarada en el esquema.',
    },
  ]);
  assert.equal(JSON.stringify(errorResult).includes('hidden'), false);
});

test('evaluates all dependency forms only from present and valid variables', () => {
  const compiled = compileSchema({
    version: 'v1',
    variables: {
      A: { type: 'string' },
      B: { type: 'string' },
      C: { type: 'number' },
      D: { type: 'string' },
    },
    dependencies: [
      { kind: 'allOrNone', keys: ['A', 'B'] },
      { kind: 'requires', if: 'A', then: 'C' },
      { kind: 'forbids', if: 'A', then: 'D' },
    ],
  });
  const result = validateConfiguration(compiled, { A: 'yes', C: 'invalid', D: 'also' });

  assert.deepEqual(
    result.error.issues.map((entry) => [entry.code, entry.key, entry.keys]),
    [
      ['E_CONFIG_ALL_OR_NONE', undefined, ['A', 'B']],
      ['E_CONFIG_FORBIDS', 'A', undefined],
      ['E_CONFIG_REQUIRES', 'A', undefined],
      ['E_CONFIG_TYPE', 'C', undefined],
    ],
  );
});

test('accepts a Record input and rejects non-string raw values', () => {
  const compiled = compileSchema({ version: 'v1', variables: { VALUE: { type: 'string' } } });
  assert.equal(validateConfiguration(compiled, { VALUE: 'ok' }).valid, true);
  assert.throws(() => validateConfiguration(compiled, new Map([['VALUE', 1]])), /cadenas/);
});
