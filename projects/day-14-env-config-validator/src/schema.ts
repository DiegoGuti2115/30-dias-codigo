import { z } from 'zod';

import {
  SchemaCompilationError,
  schemaIssue,
  type SchemaErrorCode,
  type SchemaIssue,
} from './errors.js';

const variableNamePattern = /^[A-Za-z_][A-Za-z0-9_]*$/;
const protocolPattern = /^[a-z][a-z0-9+.-]*:$/;
const transformNames = ['trim', 'lowercase', 'uppercase', 'splitComma', 'parseJson'] as const;

export type TransformName = (typeof transformNames)[number];
export type VariableType = 'string' | 'number' | 'boolean' | 'enum' | 'url' | 'list';
export type UnknownKeysPolicy = 'allow' | 'warn' | 'error';

export interface CompiledPattern {
  readonly source: string;
  readonly flags: string;
  readonly expression: RegExp;
}

interface CompiledVariableBase {
  readonly name: string;
  readonly type: VariableType;
  readonly required: boolean;
  readonly secret: boolean;
  readonly transforms: readonly TransformName[];
  readonly defaultValue?: string | number | boolean | readonly (string | number | boolean)[];
  readonly description?: string;
}

export interface CompiledStringVariable extends CompiledVariableBase {
  readonly type: 'string';
  readonly minLength?: number;
  readonly maxLength?: number;
  readonly pattern?: CompiledPattern;
}

export interface CompiledNumberVariable extends CompiledVariableBase {
  readonly type: 'number';
  readonly integer?: boolean;
  readonly min?: number;
  readonly max?: number;
}

export interface CompiledBooleanVariable extends CompiledVariableBase {
  readonly type: 'boolean';
}

export interface CompiledEnumVariable extends CompiledVariableBase {
  readonly type: 'enum';
  readonly values: readonly string[];
}

export interface CompiledUrlVariable extends CompiledVariableBase {
  readonly type: 'url';
  readonly protocols: readonly string[];
}

export interface CompiledListVariable extends CompiledVariableBase {
  readonly type: 'list';
  readonly items: 'string' | 'number' | 'boolean';
  readonly minItems?: number;
  readonly maxItems?: number;
}

export type CompiledVariable =
  | CompiledStringVariable
  | CompiledNumberVariable
  | CompiledBooleanVariable
  | CompiledEnumVariable
  | CompiledUrlVariable
  | CompiledListVariable;

export type CompiledDependency =
  | { readonly kind: 'allOrNone'; readonly keys: readonly string[] }
  | { readonly kind: 'requires' | 'forbids'; readonly if: string; readonly then: string };

export interface ValidationPlan {
  readonly version: 'v1';
  readonly unknownKeys: UnknownKeysPolicy;
  readonly variables: ReadonlyMap<string, CompiledVariable>;
  readonly dependencies: readonly CompiledDependency[];
}

const commonVariable = {
  required: z.boolean().optional(),
  secret: z.boolean().optional(),
  default: z.union([z.string(), z.number().finite(), z.boolean(), z.array(z.unknown())]).optional(),
  transforms: z.array(z.enum(transformNames)).optional(),
  description: z.string().optional(),
};

const patternSchema = z
  .object({ source: z.string().min(1).max(256), flags: z.string().optional() })
  .strict();

const variableSchema = z.discriminatedUnion('type', [
  z
    .object({
      type: z.literal('string'),
      ...commonVariable,
      minLength: z.number().int().nonnegative().optional(),
      maxLength: z.number().int().nonnegative().optional(),
      pattern: patternSchema.optional(),
    })
    .strict(),
  z
    .object({
      type: z.literal('number'),
      ...commonVariable,
      integer: z.boolean().optional(),
      min: z.number().finite().optional(),
      max: z.number().finite().optional(),
    })
    .strict(),
  z.object({ type: z.literal('boolean'), ...commonVariable }).strict(),
  z
    .object({
      type: z.literal('enum'),
      ...commonVariable,
      values: z.array(z.string().min(1)).min(1).max(100),
    })
    .strict(),
  z
    .object({
      type: z.literal('url'),
      ...commonVariable,
      protocols: z.array(z.string()).min(1).optional(),
    })
    .strict(),
  z
    .object({
      type: z.literal('list'),
      ...commonVariable,
      items: z.enum(['string', 'number', 'boolean']),
      minItems: z.number().int().nonnegative().optional(),
      maxItems: z.number().int().nonnegative().optional(),
    })
    .strict(),
]);

const dependencySchema = z.discriminatedUnion('kind', [
  z.object({ kind: z.literal('allOrNone'), keys: z.array(z.string()).min(2).max(50) }).strict(),
  z.object({ kind: z.literal('requires'), if: z.string(), then: z.string() }).strict(),
  z.object({ kind: z.literal('forbids'), if: z.string(), then: z.string() }).strict(),
]);

const documentSchema = z
  .object({
    version: z.literal('v1'),
    variables: z.record(variableSchema).refine((value) => Object.keys(value).length > 0),
    unknownKeys: z.enum(['allow', 'warn', 'error']).optional(),
    dependencies: z.array(dependencySchema).optional(),
  })
  .strict();

type ParsedDocument = z.infer<typeof documentSchema>;
type ParsedVariable = z.infer<typeof variableSchema>;

/** Parses a JSON document and compiles the closed v1 schema into an immutable plan. */
export function compileSchemaJson(source: string): ValidationPlan {
  let document: unknown;

  try {
    document = JSON.parse(source) as unknown;
  } catch {
    throw new SchemaCompilationError('E_SCHEMA_JSON_PARSE', [
      schemaIssue('E_SCHEMA_JSON_PARSE', '$', 'El documento de esquema no contiene JSON válido.'),
    ]);
  }

  return compileSchema(document);
}

/** Validates an already parsed JSON value and compiles it without I/O or process access. */
export function compileSchema(document: unknown): ValidationPlan {
  const parsed = documentSchema.safeParse(document);
  if (!parsed.success) {
    throw new SchemaCompilationError(
      isUnknownFieldError(parsed.error.issues) ? 'E_SCHEMA_UNKNOWN_FIELD' : 'E_SCHEMA_INVALID',
      parsed.error.issues.map((issue) =>
        schemaIssue(
          issue.code === 'unrecognized_keys' ? 'E_SCHEMA_UNKNOWN_FIELD' : 'E_SCHEMA_INVALID',
          formatPath(issue.path),
          issue.message,
        ),
      ),
    );
  }

  const issues: SchemaIssue[] = [];
  const variables = new Map<string, CompiledVariable>();

  for (const [name, variable] of Object.entries(parsed.data.variables)) {
    validateVariableName(name, issues);
    const compiled = compileVariable(name, variable, issues);
    if (compiled !== undefined) {
      variables.set(name, compiled);
    }
  }

  const dependencies = compileDependencies(parsed.data, variables, issues);

  if (issues.length > 0) {
    throw new SchemaCompilationError(selectErrorCode(issues), sortIssues(issues));
  }

  return Object.freeze({
    version: 'v1',
    unknownKeys: parsed.data.unknownKeys ?? 'warn',
    variables: readonlyMap(variables),
    dependencies: Object.freeze(dependencies),
  });
}

function compileVariable(
  name: string,
  variable: ParsedVariable,
  issues: SchemaIssue[],
): CompiledVariable | undefined {
  const path = `$.variables.${name}`;
  const transforms = Object.freeze([...(variable.transforms ?? [])]);
  validateTransforms(variable.type, transforms, path, issues);

  switch (variable.type) {
    case 'string': {
      if (
        variable.minLength !== undefined &&
        variable.maxLength !== undefined &&
        variable.minLength > variable.maxLength
      ) {
        invalid(issues, path, 'minLength no puede superar maxLength.');
      }
      const pattern = compilePattern(variable.pattern, `${path}.pattern`, issues);
      const compiled: CompiledStringVariable = freezeVariable({
        name,
        type: 'string',
        required: variable.required ?? false,
        secret: variable.secret ?? false,
        transforms,
        ...(variable.description === undefined ? {} : { description: variable.description }),
        ...(variable.minLength === undefined ? {} : { minLength: variable.minLength }),
        ...(variable.maxLength === undefined ? {} : { maxLength: variable.maxLength }),
        ...(pattern === undefined ? {} : { pattern }),
      });
      return applyAndValidateDefault(compiled, variable.default, path, issues);
    }
    case 'number': {
      if (variable.min !== undefined && variable.max !== undefined && variable.min > variable.max)
        invalid(issues, path, 'min no puede superar max.');
      const compiled: CompiledNumberVariable = freezeVariable({
        name,
        type: 'number',
        required: variable.required ?? false,
        secret: variable.secret ?? false,
        transforms,
        ...(variable.description === undefined ? {} : { description: variable.description }),
        ...(variable.integer === undefined ? {} : { integer: variable.integer }),
        ...(variable.min === undefined ? {} : { min: variable.min }),
        ...(variable.max === undefined ? {} : { max: variable.max }),
      });
      return applyAndValidateDefault(compiled, variable.default, path, issues);
    }
    case 'boolean': {
      const compiled: CompiledBooleanVariable = freezeVariable({
        name,
        type: 'boolean',
        required: variable.required ?? false,
        secret: variable.secret ?? false,
        transforms,
        ...(variable.description === undefined ? {} : { description: variable.description }),
      });
      return applyAndValidateDefault(compiled, variable.default, path, issues);
    }
    case 'enum': {
      if (new Set(variable.values).size !== variable.values.length)
        invalid(issues, `${path}.values`, 'values no puede contener elementos duplicados.');
      const compiled: CompiledEnumVariable = freezeVariable({
        name,
        type: 'enum',
        required: variable.required ?? false,
        secret: variable.secret ?? false,
        transforms,
        values: Object.freeze([...variable.values]),
        ...(variable.description === undefined ? {} : { description: variable.description }),
      });
      return applyAndValidateDefault(compiled, variable.default, path, issues);
    }
    case 'url': {
      const protocols = variable.protocols ?? ['http:', 'https:'];
      if (
        new Set(protocols).size !== protocols.length ||
        protocols.some((protocol) => !protocolPattern.test(protocol))
      )
        invalid(
          issues,
          `${path}.protocols`,
          'protocols debe contener protocolos distintos en minúscula y con sufijo ":".',
        );
      const compiled: CompiledUrlVariable = freezeVariable({
        name,
        type: 'url',
        required: variable.required ?? false,
        secret: variable.secret ?? false,
        transforms,
        protocols: Object.freeze([...protocols]),
        ...(variable.description === undefined ? {} : { description: variable.description }),
      });
      return applyAndValidateDefault(compiled, variable.default, path, issues);
    }
    case 'list': {
      if (
        variable.minItems !== undefined &&
        variable.maxItems !== undefined &&
        variable.minItems > variable.maxItems
      )
        invalid(issues, path, 'minItems no puede superar maxItems.');
      const compiled: CompiledListVariable = freezeVariable({
        name,
        type: 'list',
        required: variable.required ?? false,
        secret: variable.secret ?? false,
        transforms,
        items: variable.items,
        ...(variable.description === undefined ? {} : { description: variable.description }),
        ...(variable.minItems === undefined ? {} : { minItems: variable.minItems }),
        ...(variable.maxItems === undefined ? {} : { maxItems: variable.maxItems }),
      });
      return applyAndValidateDefault(compiled, variable.default, path, issues);
    }
  }
}

function validateVariableName(name: string, issues: SchemaIssue[]): void {
  if (!variableNamePattern.test(name))
    invalid(issues, `$.variables.${name}`, 'El nombre de variable no cumple el formato permitido.');
}

function validateTransforms(
  type: VariableType,
  transforms: readonly TransformName[],
  path: string,
  issues: SchemaIssue[],
): void {
  for (const transform of transforms) {
    if (transforms.filter((current) => current === transform).length > 1)
      invalid(issues, `${path}.transforms`, `La transformación ${transform} no puede repetirse.`);
  }
  if (
    type !== 'list' &&
    transforms.some((transform) => transform === 'splitComma' || transform === 'parseJson')
  )
    invalid(issues, `${path}.transforms`, 'splitComma y parseJson solo son válidas para list.');
  if (transforms.includes('splitComma') && transforms.includes('parseJson'))
    invalid(issues, `${path}.transforms`, 'splitComma no puede combinarse con parseJson.');
}

function compilePattern(
  pattern: { source: string; flags?: string | undefined } | undefined,
  path: string,
  issues: SchemaIssue[],
): CompiledPattern | undefined {
  if (pattern === undefined) return undefined;
  const flags = pattern.flags ?? '';
  if (!/^[imu]*$/.test(flags) || new Set(flags).size !== flags.length) {
    issues.push(
      schemaIssue(
        'E_SCHEMA_INVALID_PATTERN',
        `${path}.flags`,
        'flags solo puede contener i, m y u sin repetición.',
      ),
    );
    return undefined;
  }
  try {
    return Object.freeze({
      source: pattern.source,
      flags,
      expression: new RegExp(pattern.source, flags),
    });
  } catch {
    issues.push(
      schemaIssue('E_SCHEMA_INVALID_PATTERN', path, 'No se pudo construir el patrón RegExp.'),
    );
    return undefined;
  }
}

function applyAndValidateDefault<T extends CompiledVariable>(
  variable: T,
  value: unknown,
  path: string,
  issues: SchemaIssue[],
): T {
  if (value === undefined) return variable;

  const transformed =
    typeof value === 'string' ? applyTransforms(value, variable.transforms) : value;
  const converted = convertDefault(variable, transformed);
  if (converted === undefined || !isCompatibleDefault(variable, converted)) {
    invalid(
      issues,
      `${path}.default`,
      'default no es compatible con el tipo, las transformaciones o las restricciones declaradas.',
    );
    return variable;
  }

  return freezeVariable({ ...variable, defaultValue: freezeDefault(converted) }) as T;
}

function applyTransforms(
  value: string,
  transforms: readonly TransformName[],
): string | readonly string[] {
  let current: string | readonly string[] = value;

  for (const transform of transforms) {
    if (typeof current !== 'string') break;

    if (transform === 'trim') current = current.trim();
    if (transform === 'lowercase') current = current.toLowerCase();
    if (transform === 'uppercase') current = current.toUpperCase();
    if (transform === 'splitComma') {
      current = Object.freeze(current.split(',').map((item) => item.trim()));
    }
  }

  return current;
}

function isCompatibleDefault(
  variable: CompiledVariable,
  converted: string | number | boolean | readonly unknown[],
): boolean {
  switch (variable.type) {
    case 'string':
      return (
        typeof converted === 'string' &&
        (variable.minLength === undefined || converted.length >= variable.minLength) &&
        (variable.maxLength === undefined || converted.length <= variable.maxLength) &&
        (variable.pattern === undefined || variable.pattern.expression.test(converted))
      );
    case 'number':
      return (
        typeof converted === 'number' &&
        (!variable.integer || Number.isSafeInteger(converted)) &&
        (variable.min === undefined || converted >= variable.min) &&
        (variable.max === undefined || converted <= variable.max)
      );
    case 'boolean':
      return typeof converted === 'boolean';
    case 'enum':
      return typeof converted === 'string' && variable.values.includes(converted);
    case 'url':
      if (typeof converted !== 'string') return false;
      try {
        return variable.protocols.includes(new URL(converted).protocol);
      } catch {
        return false;
      }
    case 'list':
      return (
        Array.isArray(converted) &&
        (variable.minItems === undefined || converted.length >= variable.minItems) &&
        (variable.maxItems === undefined || converted.length <= variable.maxItems) &&
        converted.every(
          (item: unknown) =>
            typeof item === variable.items &&
            (variable.items !== 'number' || Number.isFinite(item)),
        )
      );
  }
}

function convertDefault(
  variable: CompiledVariable,
  value: unknown,
): string | number | boolean | readonly unknown[] | undefined {
  if (variable.type === 'list') {
    if (Array.isArray(value)) return value;
    if (typeof value !== 'string') return undefined;
    try {
      const parsed: unknown = JSON.parse(value);
      return Array.isArray(parsed) ? parsed : undefined;
    } catch {
      return undefined;
    }
  }

  if (variable.type === 'string' || variable.type === 'enum' || variable.type === 'url') {
    return typeof value === 'string' ? value : undefined;
  }
  if (variable.type === 'number') {
    if (typeof value === 'number' && Number.isFinite(value)) return value;
    if (typeof value !== 'string' || value.trim() === '') return undefined;
    const converted = Number(value);
    return Number.isFinite(converted) ? converted : undefined;
  }
  if (typeof value === 'boolean') return value;
  return value === 'true' ? true : value === 'false' ? false : undefined;
}

function compileDependencies(
  document: ParsedDocument,
  variables: ReadonlyMap<string, CompiledVariable>,
  issues: SchemaIssue[],
): CompiledDependency[] {
  const seen = new Set<string>();
  const dependencies: CompiledDependency[] = [];
  for (const [index, dependency] of (document.dependencies ?? []).entries()) {
    const path = `$.dependencies[${index}]`;
    const key = JSON.stringify(dependency);
    if (seen.has(key))
      issues.push(
        schemaIssue(
          'E_SCHEMA_DUPLICATE_DEPENDENCY',
          path,
          'La regla de dependencia está duplicada.',
        ),
      );
    seen.add(key);
    const references =
      dependency.kind === 'allOrNone' ? dependency.keys : [dependency.if, dependency.then];
    for (const reference of references)
      if (!variables.has(reference))
        issues.push(
          schemaIssue(
            'E_SCHEMA_UNKNOWN_REFERENCE',
            path,
            `La variable referenciada ${reference} no existe.`,
          ),
        );
    if (new Set(references).size !== references.length)
      invalid(issues, path, 'Una regla de dependencia no puede repetir una clave.');
    dependencies.push(
      Object.freeze(
        dependency.kind === 'allOrNone'
          ? { kind: dependency.kind, keys: Object.freeze([...dependency.keys]) }
          : { kind: dependency.kind, if: dependency.if, then: dependency.then },
      ),
    );
  }
  return dependencies;
}

function freezeDefault(
  value: unknown,
): string | number | boolean | readonly (string | number | boolean)[] {
  return Array.isArray(value)
    ? (Object.freeze([...value]) as readonly (string | number | boolean)[])
    : (value as string | number | boolean);
}

function freezeVariable<T extends CompiledVariable>(variable: T): T {
  return Object.freeze(variable);
}

function readonlyMap<T>(source: Map<string, T>): ReadonlyMap<string, T> {
  const target = new Map(source);

  return new Proxy(target, {
    get(map, property) {
      if (property === 'set' || property === 'delete' || property === 'clear') {
        return () => {
          throw new TypeError('El plan de validación es inmutable.');
        };
      }
      if (property === 'size') return map.size;

      const value = Reflect.get(map, property, map);
      return typeof value === 'function' ? value.bind(map) : value;
    },
  }) as ReadonlyMap<string, T>;
}

function invalid(issues: SchemaIssue[], path: string, message: string): void {
  issues.push(schemaIssue('E_SCHEMA_INVALID', path, message));
}

function formatPath(path: readonly (string | number)[]): string {
  return path.reduce<string>(
    (current, segment) =>
      typeof segment === 'number'
        ? `${current}[${segment}]`
        : current === '$'
          ? `$.${segment}`
          : `${current}.${segment}`,
    '$',
  );
}

function isUnknownFieldError(issues: readonly z.ZodIssue[]): boolean {
  return issues.some((issue) => issue.code === 'unrecognized_keys');
}

function selectErrorCode(issues: readonly SchemaIssue[]): SchemaErrorCode {
  if (issues.some((issue) => issue.code === 'E_SCHEMA_INVALID_PATTERN')) {
    return 'E_SCHEMA_INVALID_PATTERN';
  }
  if (issues.some((issue) => issue.code === 'E_SCHEMA_UNKNOWN_REFERENCE')) {
    return 'E_SCHEMA_UNKNOWN_REFERENCE';
  }
  if (issues.some((issue) => issue.code === 'E_SCHEMA_DUPLICATE_DEPENDENCY')) {
    return 'E_SCHEMA_DUPLICATE_DEPENDENCY';
  }
  if (issues.some((issue) => issue.code === 'E_SCHEMA_UNKNOWN_FIELD')) {
    return 'E_SCHEMA_UNKNOWN_FIELD';
  }
  return 'E_SCHEMA_INVALID';
}

function sortIssues(issues: readonly SchemaIssue[]): readonly SchemaIssue[] {
  return [...issues].sort(
    (left, right) =>
      left.path.localeCompare(right.path) ||
      left.code.localeCompare(right.code) ||
      left.message.localeCompare(right.message),
  );
}
