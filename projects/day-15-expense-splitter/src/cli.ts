#!/usr/bin/env node

import { readFile, stat } from 'node:fs/promises';
import process from 'node:process';

import { splitExpenses } from './expense-splitter.js';
import { DomainValidationError } from './validation.js';

const HELP_TEXT = `Uso: expense-splitter <ruta-entrada.json>

Calcula balances y transferencias de un reparto igualitario de gastos.
Ejemplo: expense-splitter ./data/fixtures/viaje.json`;

const ERROR_MESSAGES = {
  usage: 'La invocación no cumple el uso esperado.',
  input: 'No se pudo preparar el archivo de entrada.',
  validation: 'Los datos no cumplen el contrato v1.',
  internal: 'No se pudo calcular el reparto.',
} as const;

type PublicErrorCode =
  | 'E_USAGE_ARGUMENTS'
  | 'E_USAGE_UNKNOWN_OPTION'
  | 'E_INPUT_READ'
  | 'E_INPUT_NOT_REGULAR'
  | 'E_INPUT_NOT_UTF8'
  | 'E_INPUT_JSON_PARSE'
  | 'E_INTERNAL';

type PublicErrorCategory = keyof typeof ERROR_MESSAGES;

interface PublicError {
  readonly error: {
    readonly code: string;
    readonly category: PublicErrorCategory;
    readonly message: string;
    readonly issues: readonly unknown[];
  };
}

class InputError extends Error {
  public constructor(public readonly code: Extract<PublicErrorCode, `E_INPUT_${string}`>) {
    super(ERROR_MESSAGES.input);
    this.name = 'InputError';
  }
}

function publicError(
  code: string,
  category: PublicErrorCategory,
  issues: readonly unknown[] = [],
): PublicError {
  return {
    error: {
      code,
      category,
      message: ERROR_MESSAGES[category],
      issues,
    },
  };
}

function isHelpArgument(argument: string): boolean {
  return argument === '--help' || argument === '-h';
}

function isOption(argument: string): boolean {
  return argument.startsWith('-');
}

function writeJson(stream: NodeJS.WriteStream, value: unknown): void {
  stream.write(`${JSON.stringify(value)}\n`);
}

async function readUtf8File(path: string): Promise<string> {
  try {
    const details = await stat(path);
    if (!details.isFile()) {
      throw new InputError('E_INPUT_NOT_REGULAR');
    }

    const bytes = await readFile(path);
    try {
      const text = new TextDecoder('utf-8', { fatal: true }).decode(bytes);
      return text.startsWith('\uFEFF') ? text.slice(1) : text;
    } catch {
      throw new InputError('E_INPUT_NOT_UTF8');
    }
  } catch (error: unknown) {
    if (error instanceof InputError) {
      throw error;
    }

    throw new InputError('E_INPUT_READ');
  }
}

function parseJson(source: string): unknown {
  try {
    return JSON.parse(source) as unknown;
  } catch {
    throw new InputError('E_INPUT_JSON_PARSE');
  }
}

export async function run(arguments_: readonly string[]): Promise<number> {
  if (arguments_.length === 1 && isHelpArgument(arguments_[0] ?? '')) {
    process.stdout.write(`${HELP_TEXT}\n`);
    return 0;
  }

  if (arguments_.some((argument) => isOption(argument) && !isHelpArgument(argument))) {
    writeJson(process.stderr, publicError('E_USAGE_UNKNOWN_OPTION', 'usage'));
    return 2;
  }

  if (arguments_.length !== 1 || arguments_.some(isHelpArgument)) {
    writeJson(process.stderr, publicError('E_USAGE_ARGUMENTS', 'usage'));
    return 2;
  }

  const [inputPath] = arguments_;
  if (inputPath === undefined) {
    writeJson(process.stderr, publicError('E_INTERNAL', 'internal'));
    return 1;
  }

  try {
    const document = parseJson(await readUtf8File(inputPath));
    writeJson(process.stdout, splitExpenses(document));
    return 0;
  } catch (error: unknown) {
    if (error instanceof InputError) {
      writeJson(process.stderr, publicError(error.code, 'input'));
      return 3;
    }

    if (error instanceof DomainValidationError) {
      const code = error.issues[0]?.code ?? 'E_VALIDATION_ROOT';
      writeJson(process.stderr, publicError(code, 'validation', error.issues));
      return 4;
    }

    writeJson(process.stderr, publicError('E_INTERNAL', 'internal'));
    return 1;
  }
}

process.exitCode = await run(process.argv.slice(2));
