import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

const projectDirectory = fileURLToPath(new URL('..', import.meta.url));
const cliPath = join(projectDirectory, 'dist', 'cli.js');
const fixturePath = join(projectDirectory, 'data', 'fixtures', 'viaje.json');

function runCli(arguments_) {
  return spawnSync(process.execPath, [cliPath, ...arguments_], {
    cwd: projectDirectory,
    encoding: 'utf8',
  });
}

function temporaryFile(name, content, encoding = 'utf8') {
  const directory = mkdtempSync(join(tmpdir(), 'expense-splitter-'));
  const path = join(directory, name);
  writeFileSync(path, content, encoding);
  return { path, remove: () => rmSync(directory, { force: true, recursive: true }) };
}

test('prints help only to stdout and maps usage errors to exit code 2', () => {
  const help = runCli(['--help']);
  assert.equal(help.status, 0);
  assert.equal(help.stderr, '');
  assert.equal(
    help.stdout,
    'Uso: expense-splitter <ruta-entrada.json>\n\n' +
      'Calcula balances y transferencias de un reparto igualitario de gastos.\n' +
      'Ejemplo: expense-splitter ./data/fixtures/viaje.json\n',
  );

  for (const arguments_ of [[], ['one.json', 'two.json'], ['--format', 'json'], ['-h', 'extra']]) {
    const result = runCli(arguments_);
    assert.equal(result.status, 2);
    assert.equal(result.stdout, '');
    assert.equal(JSON.parse(result.stderr).error.category, 'usage');
  }
});

test('emits the committed fixture result deterministically through the public CLI', () => {
  const expected = JSON.parse(
    readFileSync(join(projectDirectory, 'data', 'expected', 'viaje-result.json'), 'utf8'),
  );
  const first = runCli([fixturePath]);
  const second = runCli([fixturePath]);

  for (const result of [first, second]) {
    assert.equal(result.status, 0);
    assert.equal(result.stderr, '');
    assert.deepEqual(JSON.parse(result.stdout), expected);
  }
  assert.equal(first.stdout, second.stdout);
});

test('maps file, encoding, JSON, and validation failures to safe public envelopes', () => {
  const missing = runCli(['missing.json']);
  assert.equal(missing.status, 3);
  assert.equal(missing.stdout, '');
  assert.equal(JSON.parse(missing.stderr).error.code, 'E_INPUT_READ');

  const directory = mkdtempSync(join(tmpdir(), 'expense-splitter-boundaries-'));
  const invalidUtf8 = join(directory, 'invalid-utf8.json');
  const notAFile = join(directory, 'directory');
  writeFileSync(invalidUtf8, Buffer.from([0xc3, 0x28]));
  mkdirSync(notAFile);

  const malformed = temporaryFile('malformed.json', '{');
  const invalidDocument = temporaryFile(
    'invalid-document.json',
    JSON.stringify({ version: 'v1', currency: 'EUR', participants: [], expenses: [] }),
  );
  try {
    for (const path of [invalidUtf8, notAFile]) {
      const result = runCli([path]);
      assert.equal(result.status, 3);
      assert.equal(result.stdout, '');
      assert.equal(JSON.parse(result.stderr).error.category, 'input');
    }

    const malformedResult = runCli([malformed.path]);
    assert.equal(malformedResult.status, 3);
    assert.equal(JSON.parse(malformedResult.stderr).error.code, 'E_INPUT_JSON_PARSE');

    const validationResult = runCli([invalidDocument.path]);
    assert.equal(validationResult.status, 4);
    assert.equal(validationResult.stdout, '');
    const error = JSON.parse(validationResult.stderr).error;
    assert.equal(error.category, 'validation');
    assert.equal(error.code, 'E_VALIDATION_EXPENSES');
    assert.deepEqual(
      error.issues.map((issue) => issue.code),
      ['E_VALIDATION_EXPENSES', 'E_VALIDATION_PARTICIPANTS'],
    );
  } finally {
    rmSync(directory, { force: true, recursive: true });
    malformed.remove();
    invalidDocument.remove();
  }
});

test('accepts an initial UTF-8 BOM without altering the result', () => {
  const source = temporaryFile(
    'bom.json',
    `\uFEFF${JSON.stringify({
      version: 'v1',
      currency: 'USD',
      participants: [
        { id: 'ana', name: 'Ana' },
        { id: 'bruno', name: 'Bruno' },
      ],
      expenses: [
        {
          id: 'single',
          description: 'Gasto',
          amountMinor: 1,
          paidBy: 'ana',
          splitAmong: ['ana', 'bruno'],
        },
      ],
    })}`,
  );
  try {
    const result = runCli([source.path]);
    assert.equal(result.status, 0);
    assert.equal(result.stderr, '');
    assert.equal(JSON.parse(result.stdout).currency, 'USD');
  } finally {
    source.remove();
  }
});
