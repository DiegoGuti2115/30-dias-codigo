import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const cliPath = fileURLToPath(new URL('../dist/cli.js', import.meta.url));
const helpText = `Uso: slug-generator <texto>

Convierte un único texto en un slug ASCII en minúsculas.
Ejemplo: slug-generator "Guía rápida de TypeScript"\n`;

function runCli(arguments_ = []) {
  return spawnSync(process.execPath, [cliPath, ...arguments_], {
    encoding: 'utf8',
  });
}

function assertCliResult(arguments_, expected) {
  const result = runCli(arguments_);

  assert.equal(result.error, undefined);
  assert.equal(result.status, expected.status);
  assert.equal(result.stdout, expected.stdout);
  assert.equal(result.stderr, expected.stderr);
}

test('emite slugs canónicos por la salida estándar y termina correctamente', () => {
  for (const [input, slug] of [
    ['  Guía rápida de TypeScript  ', 'guia-rapida-de-typescript'],
    ['API_v2: novedades', 'api-v2-novedades'],
    ['Straße & Æsir', 'strasse-aesir'],
    ['uno中文dos', 'uno-dos'],
    ['Málaga—Sevilla / 2026', 'malaga-sevilla-2026'],
  ]) {
    assertCliResult([input], {
      status: 0,
      stdout: `${slug}\n`,
      stderr: '',
    });
  }
});

test('muestra la ayuda exacta mediante ambas opciones admitidas', () => {
  for (const helpOption of ['--help', '-h']) {
    assertCliResult([helpOption], {
      status: 0,
      stdout: helpText,
      stderr: '',
    });
  }
});

test('rechaza la ausencia de texto sin escribir salida estándar', () => {
  assertCliResult([], {
    status: 2,
    stdout: '',
    stderr: 'Error: falta el argumento <texto>. Usa --help para consultar el uso.\n',
  });
});

test('rechaza múltiples argumentos y ayuda combinada con texto', () => {
  for (const arguments_ of [
    ['Guia', 'rapida'],
    ['--help', 'extra'],
    ['-h', 'extra'],
  ]) {
    assertCliResult(arguments_, {
      status: 2,
      stdout: '',
      stderr:
        'Error: se admite exactamente un argumento <texto>. Usa --help para consultar el uso.\n',
    });
  }
});

test('rechaza opciones no reconocidas sin interpretar su contenido como texto', () => {
  for (const arguments_ of [['--unicode'], ['--unicode', 'Hola'], ['-x'], ['-ñ']]) {
    assertCliResult(arguments_, {
      status: 2,
      stdout: '',
      stderr: 'Error: opción no reconocida. Usa --help para consultar el uso.\n',
    });
  }
});

test('traduce los errores de dominio a diagnósticos de terminal y código 1', () => {
  for (const [input, stderr] of [
    ['', 'Error: el texto no puede estar vacío ni contener solo espacios.\n'],
    ['   ', 'Error: el texto no puede estar vacío ni contener solo espacios.\n'],
    ['\u00a0', 'Error: el texto no puede estar vacío ni contener solo espacios.\n'],
    ['---', 'Error: el texto no contiene caracteres que puedan formar un slug.\n'],
    ['!!!', 'Error: el texto no contiene caracteres que puedan formar un slug.\n'],
    ['中文', 'Error: el texto no contiene caracteres que puedan formar un slug.\n'],
    ['😀---💡', 'Error: el texto no contiene caracteres que puedan formar un slug.\n'],
  ]) {
    assertCliResult([input], { status: 1, stdout: '', stderr });
  }
});
