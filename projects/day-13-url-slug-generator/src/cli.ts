#!/usr/bin/env node

import process from 'node:process';

import { normalizeSlug, SlugNormalizationError } from './slug.js';

const HELP_TEXT = `Uso: slug-generator <texto>

Convierte un único texto en un slug ASCII en minúsculas.
Ejemplo: slug-generator "Guía rápida de TypeScript"`;

const ERROR_MESSAGES = {
  E_USAGE_MISSING_TEXT: 'Error: falta el argumento <texto>. Usa --help para consultar el uso.',
  E_USAGE_TOO_MANY_ARGUMENTS:
    'Error: se admite exactamente un argumento <texto>. Usa --help para consultar el uso.',
  E_USAGE_UNKNOWN_OPTION: 'Error: opción no reconocida. Usa --help para consultar el uso.',
  E_INPUT_EMPTY: 'Error: el texto no puede estar vacío ni contener solo espacios.',
  E_INPUT_NOT_NORMALIZABLE: 'Error: el texto no contiene caracteres que puedan formar un slug.',
  E_INPUT_NOT_TEXT: 'Error: la entrada debe ser texto.',
  E_UNEXPECTED: 'Error: no se pudo generar el slug.',
} as const;

type CliErrorCode = keyof typeof ERROR_MESSAGES;

function writeError(code: CliErrorCode): void {
  process.stderr.write(`${ERROR_MESSAGES[code]}\n`);
}

function isHelpArgument(argument: string): boolean {
  return argument === '--help' || argument === '-h';
}

function hasUnknownOption(arguments_: readonly string[]): boolean {
  return arguments_.some((argument) => /^-{1,2}[^-]/.test(argument) && !isHelpArgument(argument));
}

function run(arguments_: readonly string[]): number {
  if (arguments_.length === 0) {
    writeError('E_USAGE_MISSING_TEXT');
    return 2;
  }

  const [argument] = arguments_;

  if (arguments_.length === 1 && argument !== undefined && isHelpArgument(argument)) {
    process.stdout.write(`${HELP_TEXT}\n`);
    return 0;
  }

  if (hasUnknownOption(arguments_)) {
    writeError('E_USAGE_UNKNOWN_OPTION');
    return 2;
  }

  if (arguments_.length !== 1) {
    writeError('E_USAGE_TOO_MANY_ARGUMENTS');
    return 2;
  }

  if (argument === undefined) {
    writeError('E_UNEXPECTED');
    return 1;
  }

  try {
    process.stdout.write(`${normalizeSlug(argument)}\n`);
    return 0;
  } catch (error: unknown) {
    if (error instanceof SlugNormalizationError) {
      writeError(error.code);
    } else {
      writeError('E_UNEXPECTED');
    }

    return 1;
  }
}

process.exitCode = run(process.argv.slice(2));
