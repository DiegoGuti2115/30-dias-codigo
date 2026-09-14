import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const projectDirectory = fileURLToPath(new URL('..', import.meta.url));
const fixtureDirectory = join(projectDirectory, 'data', 'fixtures');
const expectedDirectory = join(projectDirectory, 'data', 'expected');
const cliPath = join(projectDirectory, 'dist', 'cli.js');
const syntheticSecret = 'synthetic-regression-token';

function readJson(directory, name) {
  return JSON.parse(readFileSync(join(directory, name), 'utf8'));
}

function runFixture(environmentName, schemaName = 'valid-schema.json') {
  return spawnSync(
    process.execPath,
    [cliPath, join(fixtureDirectory, environmentName), join(fixtureDirectory, schemaName)],
    { cwd: projectDirectory, encoding: 'utf8' },
  );
}

test('matches the redacted success fixture deterministically through the public CLI', () => {
  const expected = readJson(expectedDirectory, 'valid-summary.json');
  const first = runFixture('valid-configuration.env');
  const second = runFixture('valid-configuration.env');

  for (const result of [first, second]) {
    assert.equal(result.status, 0);
    assert.equal(result.stderr, '');
    assert.deepEqual(JSON.parse(result.stdout), expected);
    assert.equal(result.stdout.includes(syntheticSecret), false);
  }
  assert.equal(first.stdout, second.stdout);
});

test('matches the ordered redacted configuration-error fixture through the public CLI', () => {
  const expected = readJson(expectedDirectory, 'invalid-configuration.json');
  const result = runFixture('invalid-configuration.env');

  assert.equal(result.status, 5);
  assert.equal(result.stdout, '');
  assert.deepEqual(JSON.parse(result.stderr), expected);
  assert.equal(result.stderr.includes(syntheticSecret), false);
});

test('keeps every committed expected response free of synthetic configuration values', () => {
  const expectedSuccess = readFileSync(join(expectedDirectory, 'valid-summary.json'), 'utf8');
  const expectedFailure = readFileSync(
    join(expectedDirectory, 'invalid-configuration.json'),
    'utf8',
  );

  assert.equal(expectedSuccess.includes(syntheticSecret), false);
  assert.equal(expectedFailure.includes(syntheticSecret), false);
});
