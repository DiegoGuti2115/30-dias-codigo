#!/usr/bin/env node

import { readFile, stat } from 'node:fs/promises';
import process from 'node:process';

import { parse as parseDotenv } from 'dotenv';

import { SchemaCompilationError, type SchemaErrorCode } from './errors.js';
import { compileSchemaJson } from './schema.js';
import { validateConfiguration } from './validator.js';

const HELP_TEXT = `Uso: env-config-validator <ruta-env> <ruta-schema>

Valida un archivo .env explícito contra un esquema JSON v1.
Ejemplo: env-config-validator ./config/demo.env ./config/schema.json`;

const ERROR_MESSAGES = {
  usage: 'La invocación no cumple el uso esperado.',
  input: 'No se pudo preparar un archivo de entrada.',
  schema: 'El esquema no cumple el contrato v1.',
  internal: 'No se pudo completar la validación.',
} as const;

type PublicErrorCode =
  | 'E_USAGE_ARGUMENTS'
  | 'E_USAGE_UNKNOWN_OPTION'
  | 'E_INPUT_READ'
  | 'E_INPUT_NOT_UTF8'
  | 'E_INPUT_ENV_PARSE'
  | SchemaErrorCode
  | 'E_INTERNAL';

type PublicErrorCategory = 'usage' | 'input' | 'schema' | 'internal';

interface PublicError {
  readonly error: {
    readonly code: PublicErrorCode;
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
  code: PublicErrorCode,
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
      throw new InputError('E_INPUT_READ');
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

function parseEnvironment(source: string): Readonly<Record<string, string>> {
  const lines = source.split(/\r\n|\n|\r/u);

  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed === '' || trimmed.startsWith('#')) {
      continue;
    }

    if (!/^[A-Za-z_][A-Za-z0-9_]*\s*=/.test(trimmed) || /^export\s+/u.test(trimmed)) {
      throw new InputError('E_INPUT_ENV_PARSE');
    }
  }

  try {
    return Object.freeze({ ...parseDotenv(source) });
  } catch {
    throw new InputError('E_INPUT_ENV_PARSE');
  }
}

export async function run(arguments_: readonly string[]): Promise<number> {
  if (arguments_.length === 1 && isHelpArgument(arguments_[0] ?? '')) {
    process.stdout.write(`${HELP_TEXT}\n`);
    return 0;
  }

  const unknownOption = arguments_.some(
    (argument) => isOption(argument) && !isHelpArgument(argument),
  );
  if (unknownOption) {
    writeJson(process.stderr, publicError('E_USAGE_UNKNOWN_OPTION', 'usage'));
    return 2;
  }

  if (arguments_.length !== 2 || arguments_.some(isHelpArgument)) {
    writeJson(process.stderr, publicError('E_USAGE_ARGUMENTS', 'usage'));
    return 2;
  }

  const [environmentPath, schemaPath] = arguments_;
  if (environmentPath === undefined || schemaPath === undefined) {
    writeJson(process.stderr, publicError('E_INTERNAL', 'internal'));
    return 1;
  }

  try {
    const [environmentSource, schemaSource] = await Promise.all([
      readUtf8File(environmentPath),
      readUtf8File(schemaPath),
    ]);
    const configuration = parseEnvironment(environmentSource);
    const plan = compileSchemaJson(schemaSource);
    const result = validateConfiguration(plan, configuration);

    if ('valid' in result) {
      writeJson(process.stdout, result);
      return 0;
    }

    writeJson(process.stderr, result);
    return 5;
  } catch (error: unknown) {
    if (error instanceof InputError) {
      writeJson(process.stderr, publicError(error.code, 'input'));
      return 3;
    }

    if (error instanceof SchemaCompilationError) {
      writeJson(process.stderr, publicError(error.code, 'schema', error.issues));
      return 4;
    }

    writeJson(process.stderr, publicError('E_INTERNAL', 'internal'));
    return 1;
  }
}

process.exitCode = await run(process.argv.slice(2));
