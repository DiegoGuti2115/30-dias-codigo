import assert from 'node:assert/strict';
import test from 'node:test';

import { SchemaCompilationError } from '../dist/errors.js';
import { compileSchema, compileSchemaJson } from '../dist/schema.js';

test('compiles a valid v1 document into a plan detached from the input document', () => {
  const document = {
    version: 'v1',
    unknownKeys: 'error',
    variables: {
      APP_PORT: {
        type: 'number',
        required: true,
        integer: true,
        min: 1,
        max: 65535,
        default: '3000',
        transforms: ['trim'],
      },
      TAGS: {
        type: 'list',
        items: 'string',
        default: ' api, web ',
        transforms: ['splitComma'],
      },
      API_URL: {
        type: 'url',
        default: 'https://example.test',
      },
    },
    dependencies: [{ kind: 'requires', if: 'API_URL', then: 'APP_PORT' }],
  };

  const plan = compileSchema(document);
  document.variables.APP_PORT.min = 2;

  assert.equal(plan.version, 'v1');
  assert.equal(plan.unknownKeys, 'error');
  assert.equal(plan.variables.get('APP_PORT')?.type, 'number');
  assert.deepEqual(plan.variables.get('TAGS')?.defaultValue, ['api', 'web']);
  assert.deepEqual(plan.dependencies, [{ kind: 'requires', if: 'API_URL', then: 'APP_PORT' }]);
  assert.throws(() => plan.variables.set('OTHER', { type: 'string' }), /inmutable/);
});

test('reports malformed JSON independently from a schema-invalid JSON value', () => {
  assert.throws(
    () => compileSchemaJson('{'),
    (error) => error instanceof SchemaCompilationError && error.code === 'E_SCHEMA_JSON_PARSE',
  );
  assert.throws(
    () => compileSchemaJson('{"version":"v2","variables":{}}'),
    (error) => error instanceof SchemaCompilationError && error.code === 'E_SCHEMA_INVALID',
  );
});

test('rejects unknown fields and invalid variable names', () => {
  assert.throws(
    () =>
      compileSchema({
        version: 'v1',
        variables: { APP_PORT: { type: 'number', madeUp: true } },
      }),
    (error) => error instanceof SchemaCompilationError && error.code === 'E_SCHEMA_UNKNOWN_FIELD',
  );
  assert.throws(
    () => compileSchema({ version: 'v1', variables: { 'INVALID-NAME': { type: 'string' } } }),
    (error) =>
      error instanceof SchemaCompilationError &&
      error.issues.some((issue) => issue.path === '$.variables.INVALID-NAME'),
  );
});

test('rejects invalid defaults, transforms and regular expressions before runtime validation', () => {
  assert.throws(
    () =>
      compileSchema({ version: 'v1', variables: { FLAG: { type: 'boolean', default: 'yes' } } }),
    (error) => error instanceof SchemaCompilationError && error.code === 'E_SCHEMA_INVALID',
  );
  assert.throws(
    () =>
      compileSchema({
        version: 'v1',
        variables: { VALUE: { type: 'string', transforms: ['splitComma'] } },
      }),
    (error) => error instanceof SchemaCompilationError && error.code === 'E_SCHEMA_INVALID',
  );
  assert.throws(
    () =>
      compileSchema({
        version: 'v1',
        variables: { VALUE: { type: 'string', pattern: { source: '[', flags: 'g' } } },
      }),
    (error) => error instanceof SchemaCompilationError && error.code === 'E_SCHEMA_INVALID_PATTERN',
  );
});

test('rejects invalid dependency references, duplicates and repeated keys', () => {
  assert.throws(
    () =>
      compileSchema({
        version: 'v1',
        variables: { A: { type: 'string' } },
        dependencies: [{ kind: 'requires', if: 'A', then: 'MISSING' }],
      }),
    (error) =>
      error instanceof SchemaCompilationError && error.code === 'E_SCHEMA_UNKNOWN_REFERENCE',
  );
  assert.throws(
    () =>
      compileSchema({
        version: 'v1',
        variables: { A: { type: 'string' }, B: { type: 'string' } },
        dependencies: [
          { kind: 'requires', if: 'A', then: 'B' },
          { kind: 'requires', if: 'A', then: 'B' },
        ],
      }),
    (error) =>
      error instanceof SchemaCompilationError && error.code === 'E_SCHEMA_DUPLICATE_DEPENDENCY',
  );
  assert.throws(
    () =>
      compileSchema({
        version: 'v1',
        variables: { A: { type: 'string' } },
        dependencies: [{ kind: 'requires', if: 'A', then: 'A' }],
      }),
    (error) => error instanceof SchemaCompilationError && error.code === 'E_SCHEMA_INVALID',
  );
});
