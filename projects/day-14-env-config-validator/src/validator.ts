import type {
  CompiledDependency,
  CompiledListVariable,
  CompiledVariable,
  TransformName,
  ValidationPlan,
} from './schema.js';

export type RawConfiguration = Readonly<Record<string, string>> | ReadonlyMap<string, string>;

export type ConfigurationIssueCode =
  | 'E_CONFIG_REQUIRED'
  | 'E_CONFIG_UNKNOWN_KEY'
  | 'E_CONFIG_TYPE'
  | 'E_CONFIG_CONSTRAINT'
  | 'E_CONFIG_ALL_OR_NONE'
  | 'E_CONFIG_REQUIRES'
  | 'E_CONFIG_FORBIDS';

export type ConfigurationWarningCode = 'W_CONFIG_UNKNOWN_KEY';

export interface ConfigurationIssue {
  readonly code: ConfigurationIssueCode;
  readonly key?: string;
  readonly keys?: readonly string[];
  readonly rule:
    | 'required'
    | 'unknownKey'
    | 'type'
    | 'constraint'
    | 'allOrNone'
    | 'requires'
    | 'forbids';
  readonly message: string;
}

export interface ConfigurationWarning {
  readonly code: ConfigurationWarningCode;
  readonly key: string;
  readonly message: string;
}

export interface ConfigurationVariableSummary {
  readonly key: string;
  readonly status: 'absent' | 'valid';
  readonly source: 'none' | 'env' | 'default';
  readonly secret: boolean;
}

export interface ValidConfigurationResult {
  readonly valid: true;
  readonly schemaVersion: 'v1';
  readonly summary: {
    readonly declared: number;
    readonly provided: number;
    readonly defaulted: number;
    readonly warnings: number;
  };
  readonly variables: readonly ConfigurationVariableSummary[];
  readonly warnings: readonly ConfigurationWarning[];
}

export interface InvalidConfigurationResult {
  readonly error: {
    readonly code: ConfigurationIssueCode;
    readonly category: 'configuration';
    readonly message: 'La configuración no cumple el esquema.';
    readonly issues: readonly ConfigurationIssue[];
  };
}

export type ConfigurationValidationResult = ValidConfigurationResult | InvalidConfigurationResult;

type ResolvedValue = string | number | boolean | readonly (string | number | boolean)[];

type VariableState = {
  readonly variable: CompiledVariable;
  readonly source: 'none' | 'env' | 'default';
  readonly valid: boolean;
};

const typeMessage = 'El valor no cumple el tipo declarado.';
const constraintMessage = 'El valor no cumple las restricciones declaradas.';

/**
 * Evaluates already parsed environment values against an immutable schema plan.
 * It performs no I/O and never exposes configuration values in its result.
 */
export function validateConfiguration(
  plan: ValidationPlan,
  rawConfiguration: RawConfiguration,
): ConfigurationValidationResult {
  const rawValues = normalizeRawConfiguration(rawConfiguration);
  const issues: SortableIssue[] = [];
  const warnings: ConfigurationWarning[] = [];
  const states = new Map<string, VariableState>();

  for (const [key, value] of rawValues) {
    if (plan.variables.has(key)) continue;
    if (plan.unknownKeys === 'warn') {
      warnings.push(
        Object.freeze({
          code: 'W_CONFIG_UNKNOWN_KEY',
          key,
          message: 'La clave no está declarada en el esquema.',
        }),
      );
    }
    if (plan.unknownKeys === 'error') {
      issues.push(
        issue(
          'E_CONFIG_UNKNOWN_KEY',
          key,
          'unknownKey',
          'La clave no está declarada en el esquema.',
        ),
      );
    }
    void value;
  }

  for (const [key, variable] of plan.variables) {
    const hasEnvironmentValue = rawValues.has(key);
    const rawValue = rawValues.get(key);
    const source = hasEnvironmentValue
      ? 'env'
      : variable.defaultValue === undefined
        ? 'none'
        : 'default';

    if (source === 'none') {
      if (variable.required) {
        issues.push(issue('E_CONFIG_REQUIRED', key, 'required', 'Falta una variable obligatoria.'));
        states.set(key, { variable, source, valid: false });
      } else {
        states.set(key, { variable, source, valid: false });
      }
      continue;
    }

    const candidate = source === 'env' ? rawValue : variable.defaultValue;
    if (candidate === undefined) throw new Error('El plan contiene un valor de origen ausente.');
    const outcome = validateVariable(variable, candidate);
    if (outcome === 'type') issues.push(issue('E_CONFIG_TYPE', key, 'type', typeMessage));
    if (outcome === 'constraint')
      issues.push(issue('E_CONFIG_CONSTRAINT', key, 'constraint', constraintMessage));
    states.set(key, { variable, source, valid: outcome === 'valid' });
  }

  for (const [index, dependency] of plan.dependencies.entries()) {
    const dependencyIssue = validateDependency(dependency, states, index);
    if (dependencyIssue !== undefined) issues.push(dependencyIssue);
  }

  const orderedIssues = Object.freeze(
    issues
      .sort(compareIssues)
      .map(({ sortKey: _sortKey, dependencyIndex: _dependencyIndex, ...publicIssue }) =>
        Object.freeze(publicIssue),
      ),
  );
  if (orderedIssues.length > 0) {
    return Object.freeze({
      error: Object.freeze({
        code: orderedIssues[0]?.code ?? 'E_CONFIG_TYPE',
        category: 'configuration',
        message: 'La configuración no cumple el esquema.',
        issues: orderedIssues,
      }),
    });
  }

  const variables = Object.freeze(
    [...states]
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([key, state]) =>
        Object.freeze({
          key,
          status: state.source === 'none' ? 'absent' : 'valid',
          source: state.source,
          secret: state.variable.secret,
        }),
      ),
  );
  const orderedWarnings = Object.freeze(
    [...warnings].sort((left, right) => left.key.localeCompare(right.key)),
  );
  const provided = variables.filter((variable) => variable.status === 'valid').length;
  const defaulted = variables.filter((variable) => variable.source === 'default').length;

  return Object.freeze({
    valid: true,
    schemaVersion: 'v1',
    summary: Object.freeze({
      declared: variables.length,
      provided,
      defaulted,
      warnings: orderedWarnings.length,
    }),
    variables,
    warnings: orderedWarnings,
  });
}

type SortableIssue = ConfigurationIssue & {
  readonly sortKey: string;
  readonly dependencyIndex: number;
};

function normalizeRawConfiguration(
  rawConfiguration: RawConfiguration,
): ReadonlyMap<string, string> {
  const entries =
    rawConfiguration instanceof Map ? rawConfiguration.entries() : Object.entries(rawConfiguration);
  const normalized = new Map<string, string>();
  for (const [key, value] of entries) {
    if (typeof value !== 'string')
      throw new TypeError('Los valores de configuración brutos deben ser cadenas.');
    normalized.set(key, value);
  }
  return normalized;
}

function validateVariable(
  variable: CompiledVariable,
  input: string | ResolvedValue,
): 'valid' | 'type' | 'constraint' {
  const transformed =
    typeof input === 'string' ? applyTransforms(input, variable.transforms) : input;
  const converted = convertValue(variable, transformed);
  if (converted === undefined) return 'type';
  if (variable.type === 'url' && !isAbsoluteUrl(converted)) return 'type';
  return meetsConstraints(variable, converted) ? 'valid' : 'constraint';
}

function applyTransforms(
  value: string,
  transforms: readonly TransformName[],
): string | readonly string[] {
  let transformed: string | readonly string[] = value;
  for (const transform of transforms) {
    if (typeof transformed !== 'string') return transformed;
    switch (transform) {
      case 'trim':
        transformed = transformed.trim();
        break;
      case 'lowercase':
        transformed = transformed.toLowerCase();
        break;
      case 'uppercase':
        transformed = transformed.toUpperCase();
        break;
      case 'splitComma':
        transformed = Object.freeze(transformed.split(',').map((part) => part.trim()));
        break;
      case 'parseJson':
        break;
    }
  }
  return transformed;
}

function convertValue(
  variable: CompiledVariable,
  value: string | ResolvedValue | readonly string[],
): ResolvedValue | undefined {
  switch (variable.type) {
    case 'string':
    case 'enum':
    case 'url':
      return typeof value === 'string' ? value : undefined;
    case 'number':
      return convertNumber(value);
    case 'boolean':
      return typeof value === 'boolean' || value === 'true'
        ? true
        : value === 'false'
          ? false
          : undefined;
    case 'list':
      return convertList(variable, value);
  }
}

function convertNumber(value: string | ResolvedValue | readonly string[]): number | undefined {
  if (typeof value === 'number') return Number.isFinite(value) ? value : undefined;
  if (typeof value !== 'string' || value === '' || !isDecimal(value)) return undefined;
  const converted = Number(value);
  return Number.isFinite(converted) ? converted : undefined;
}

function isDecimal(value: string): boolean {
  return /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/.test(value);
}

function convertList(
  variable: CompiledListVariable,
  value: string | ResolvedValue | readonly string[],
): readonly (string | number | boolean)[] | undefined {
  let parsed: unknown;
  if (Array.isArray(value)) {
    parsed = value;
  } else if (typeof value === 'string') {
    try {
      parsed = JSON.parse(value) as unknown;
    } catch {
      return undefined;
    }
  } else {
    parsed = value;
  }
  if (!Array.isArray(parsed)) return undefined;
  if (
    !parsed.every(
      (item) =>
        typeof item === variable.items && (typeof item !== 'number' || Number.isFinite(item)),
    )
  ) {
    return undefined;
  }
  return Object.freeze([...parsed] as (string | number | boolean)[]);
}

function meetsConstraints(variable: CompiledVariable, value: ResolvedValue): boolean {
  switch (variable.type) {
    case 'string':
      return (
        typeof value === 'string' &&
        (variable.minLength === undefined || value.length >= variable.minLength) &&
        (variable.maxLength === undefined || value.length <= variable.maxLength) &&
        (variable.pattern === undefined || variable.pattern.expression.test(value))
      );
    case 'number':
      return (
        typeof value === 'number' &&
        (!variable.integer || Number.isSafeInteger(value)) &&
        (variable.min === undefined || value >= variable.min) &&
        (variable.max === undefined || value <= variable.max)
      );
    case 'boolean':
      return typeof value === 'boolean';
    case 'enum':
      return typeof value === 'string' && variable.values.includes(value);
    case 'url':
      return typeof value === 'string' && variable.protocols.includes(new URL(value).protocol);
    case 'list':
      return (
        Array.isArray(value) &&
        (variable.minItems === undefined || value.length >= variable.minItems) &&
        (variable.maxItems === undefined || value.length <= variable.maxItems)
      );
  }
}

function isAbsoluteUrl(value: ResolvedValue): value is string {
  if (typeof value !== 'string') return false;
  try {
    new URL(value);
    return true;
  } catch {
    return false;
  }
}

function validateDependency(
  dependency: CompiledDependency,
  states: ReadonlyMap<string, VariableState>,
  dependencyIndex: number,
): SortableIssue | undefined {
  if (dependency.kind === 'allOrNone') {
    const present = dependency.keys.filter((key) => states.get(key)?.valid === true);
    if (present.length === 0 || present.length === dependency.keys.length) return undefined;
    return issue(
      'E_CONFIG_ALL_OR_NONE',
      dependency.keys[0] ?? '',
      'allOrNone',
      'Las variables de la regla deben estar presentes todas o ninguna.',
      dependencyIndex,
      dependency.keys,
    );
  }
  const condition = states.get(dependency.if)?.valid === true;
  const target = states.get(dependency.then)?.valid === true;
  if (dependency.kind === 'requires' && condition && !target) {
    return issue(
      'E_CONFIG_REQUIRES',
      dependency.if,
      'requires',
      'La variable requiere otra variable válida.',
      dependencyIndex,
    );
  }
  if (dependency.kind === 'forbids' && condition && target) {
    return issue(
      'E_CONFIG_FORBIDS',
      dependency.if,
      'forbids',
      'La variable no puede coexistir con otra variable válida.',
      dependencyIndex,
    );
  }
  return undefined;
}

function issue(
  code: ConfigurationIssueCode,
  key: string,
  rule: ConfigurationIssue['rule'],
  message: string,
  dependencyIndex = -1,
  keys?: readonly string[],
): SortableIssue {
  return Object.freeze({
    code,
    ...(keys === undefined ? { key } : { keys: Object.freeze([...keys]) }),
    rule,
    message,
    sortKey: key,
    dependencyIndex,
  });
}

function compareIssues(left: SortableIssue, right: SortableIssue): number {
  return (
    left.sortKey.localeCompare(right.sortKey) ||
    left.code.localeCompare(right.code) ||
    left.dependencyIndex - right.dependencyIndex
  );
}
