import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const projectDirectory = fileURLToPath(new URL('..', import.meta.url));
const cliPath = join(projectDirectory, 'dist', 'cli.js');
const secret = 'synthetic-secret-value-never-to-be-disclosed';

function runCli(arguments_) {
  return spawnSync(process.execPath, [cliPath, ...arguments_], {
    cwd: projectDirectory,
    encoding: 'utf8',
  });
}

function fixtureFiles(environment, schema) {
  const directory = mkdtempSync(join(tmpdir(), 'env-config-validator-'));
  const environmentPath = join(directory, 'configuration.env');
  const schemaPath = join(directory, 'schema.json');
  writeFileSync(environmentPath, environment, 'utf8');
  writeFileSync(schemaPath, schema, 'utf8');

  return {
    environmentPath,
    schemaPath,
    remove: () => rmSync(directory, { force: true, recursive: true }),
  };
}

const validSchema = JSON.stringify({
  version: 'v1',
  unknownKeys: 'warn',
  variables: {
    APP_PORT: { type: 'number', required: true, integer: true, min: 1 },
    API_TOKEN: { type: 'string', required: true, secret: true, minLength: 4 },
  },
});

test('prints the stable help text only to stdout', () => {
  const result = runCli(['--help']);

  assert.equal(result.status, 0);
  assert.equal(result.stderr, '');
  assert.equal(
    result.stdout,
    'Uso: env-config-validator <ruta-env> <ruta-schema>\n\n' +
      'Valida un archivo .env explícito contra un esquema JSON v1.\n' +
      'Ejemplo: env-config-validator ./config/demo.env ./config/schema.json\n',
  );
});

test('returns a redacted JSON success envelope for explicit valid files', () => {
  const files = fixtureFiles(`APP_PORT=3000\nAPI_TOKEN=${secret}\nLEGACY_FLAG=true\n`, validSchema);

  try {
    const result = runCli([files.environmentPath, files.schemaPath]);

    assert.equal(result.status, 0);
    assert.equal(result.stderr, '');
    assert.equal(result.stdout.includes(secret), false);
    assert.deepEqual(JSON.parse(result.stdout), {
      valid: true,
      schemaVersion: 'v1',
      summary: { declared: 2, provided: 2, defaulted: 0, warnings: 1 },
      variables: [
        { key: 'API_TOKEN', status: 'valid', source: 'env', secret: true },
        { key: 'APP_PORT', status: 'valid', source: 'env', secret: false },
      ],
      warnings: [
        {
          code: 'W_CONFIG_UNKNOWN_KEY',
          key: 'LEGACY_FLAG',
          message: 'La clave no está declarada en el esquema.',
        },
      ],
    });
  } finally {
    files.remove();
  }
});

test('uses usage errors for invalid positional arguments and unknown options', () => {
  for (const arguments_ of [[], ['only-one-path'], ['--unknown'], ['-h', 'extra']]) {
    const result = runCli(arguments_);

    assert.equal(result.status, 2);
    assert.equal(result.stdout, '');
    const output = JSON.parse(result.stderr);
    assert.equal(output.error.category, 'usage');
    assert.deepEqual(output.error.issues, []);
  }
});

test('maps inaccessible inputs and invalid dotenv syntax to safe input errors', () => {
  const missing = runCli(['missing.env', 'missing.json']);
  assert.equal(missing.status, 3);
  assert.equal(missing.stdout, '');
  assert.equal(JSON.parse(missing.stderr).error.code, 'E_INPUT_READ');

  const files = fixtureFiles('export API_TOKEN=value\n', validSchema);
  try {
    const result = runCli([files.environmentPath, files.schemaPath]);
    assert.equal(result.status, 3);
    assert.equal(result.stdout, '');
    assert.equal(JSON.parse(result.stderr).error.code, 'E_INPUT_ENV_PARSE');
  } finally {
    files.remove();
  }
});

test('maps schema and configuration failures to their distinct exit codes without leaks', () => {
  const malformedSchema = fixtureFiles(`API_TOKEN=${secret}\n`, '{');
  try {
    const result = runCli([malformedSchema.environmentPath, malformedSchema.schemaPath]);
    assert.equal(result.status, 4);
    assert.equal(result.stdout, '');
    assert.equal(JSON.parse(result.stderr).error.code, 'E_SCHEMA_JSON_PARSE');
    assert.equal(result.stderr.includes(secret), false);
  } finally {
    malformedSchema.remove();
  }

  const invalidConfiguration = fixtureFiles(
    `APP_PORT=not-a-number\nAPI_TOKEN=${secret}\n`,
    validSchema,
  );
  try {
    const result = runCli([invalidConfiguration.environmentPath, invalidConfiguration.schemaPath]);
    assert.equal(result.status, 5);
    assert.equal(result.stdout, '');
    const output = JSON.parse(result.stderr);
    assert.equal(output.error.category, 'configuration');
    assert.equal(output.error.code, 'E_CONFIG_TYPE');
    assert.equal(result.stderr.includes(secret), false);
  } finally {
    invalidConfiguration.remove();
  }
});

test('covers short help, non-regular files, invalid UTF-8 and invalid schemas through public envelopes', () => {
  const shortHelp = runCli(['-h']);
  assert.equal(shortHelp.status, 0);
  assert.equal(shortHelp.stderr, '');

  const directory = mkdtempSync(join(tmpdir(), 'env-config-validator-boundaries-'));
  const regularEnvironment = join(directory, 'configuration.env');
  const invalidUtf8Environment = join(directory, 'invalid-utf8.env');
  const nonRegularEnvironment = join(directory, 'not-a-file');
  const schemaPath = join(directory, 'schema.json');
  writeFileSync(regularEnvironment, 'APP_PORT=3000\nAPI_TOKEN=synthetic-boundary-token\n', 'utf8');
  writeFileSync(invalidUtf8Environment, Buffer.from([0xc3, 0x28]));
  writeFileSync(
    schemaPath,
    JSON.stringify({ version: 'v1', variables: { VALUE: { type: 'string' } } }),
  );
  mkdirSync(nonRegularEnvironment);

  try {
    for (const environmentPath of [invalidUtf8Environment, nonRegularEnvironment]) {
      const result = runCli([environmentPath, schemaPath]);
      assert.equal(result.status, 3);
      assert.equal(result.stdout, '');
      assert.equal(JSON.parse(result.stderr).error.category, 'input');
    }

    const invalidSchema = fixtureFiles(
      'VALUE=ok\n',
      JSON.stringify({
        version: 'v1',
        variables: { VALUE: { type: 'string', script: 'return true' } },
      }),
    );
    try {
      const result = runCli([invalidSchema.environmentPath, invalidSchema.schemaPath]);
      assert.equal(result.status, 4);
      assert.equal(result.stdout, '');
      assert.equal(JSON.parse(result.stderr).error.code, 'E_SCHEMA_UNKNOWN_FIELD');
    } finally {
      invalidSchema.remove();
    }
  } finally {
    rmSync(directory, { force: true, recursive: true });
  }
});
