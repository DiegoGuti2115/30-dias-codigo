import {
  CONTRACT_VERSION,
  type DomainIssue,
  type DomainIssueCode,
  type Expense,
  type ExpenseDocument,
  type Participant,
} from './types.js';

const PARTICIPANT_ID_PATTERN = /^[A-Za-z0-9][A-Za-z0-9_-]*$/u;
const CURRENCY_PATTERN = /^[A-Z]{3}$/u;
const ROOT_KEYS = ['version', 'currency', 'participants', 'expenses'] as const;
const PARTICIPANT_KEYS = ['id', 'name'] as const;
const EXPENSE_KEYS = ['id', 'description', 'amountMinor', 'paidBy', 'splitAmong'] as const;

type UnknownRecord = Record<string, unknown>;

export class DomainValidationError extends Error {
  public readonly issues: readonly DomainIssue[];

  public constructor(issues: readonly DomainIssue[]) {
    super('Los datos no cumplen el contrato v1.');
    this.name = 'DomainValidationError';
    this.issues = [...issues].sort(compareIssues);
  }
}

export function validateExpenseDocument(input: unknown): ExpenseDocument {
  const issues: DomainIssue[] = [];
  if (!isRecord(input)) {
    issues.push(issue('E_VALIDATION_ROOT', '', 'La raíz debe ser un objeto.'));
    throw new DomainValidationError(issues);
  }

  rejectUnknownFields(input, ROOT_KEYS, '', issues);
  for (const key of ROOT_KEYS) {
    if (!(key in input)) {
      issues.push(issue('E_VALIDATION_ROOT', key, 'Falta un campo obligatorio en la raíz.'));
    }
  }
  validateVersion(input.version, issues);
  validateCurrency(input.currency, issues);
  const participants = validateParticipants(input.participants, issues);
  const participantIds = new Set(participants.map((participant) => participant.id));
  const expenses = validateExpenses(input.expenses, participantIds, issues);

  if (issues.length > 0) {
    throw new DomainValidationError(issues);
  }

  return {
    version: CONTRACT_VERSION,
    currency: input.currency as string,
    participants,
    expenses,
  };
}

function validateVersion(value: unknown, issues: DomainIssue[]): void {
  if (value !== CONTRACT_VERSION) {
    issues.push(issue('E_VALIDATION_VERSION', 'version', 'La versión debe ser exactamente v1.'));
  }
}

function validateCurrency(value: unknown, issues: DomainIssue[]): void {
  if (typeof value !== 'string' || !CURRENCY_PATTERN.test(value)) {
    issues.push(
      issue('E_VALIDATION_CURRENCY', 'currency', 'La moneda debe usar tres letras mayúsculas.'),
    );
  }
}

function validateParticipants(value: unknown, issues: DomainIssue[]): Participant[] {
  if (!Array.isArray(value) || value.length < 2 || value.length > 50) {
    issues.push(
      issue(
        'E_VALIDATION_PARTICIPANTS',
        'participants',
        'Los participantes deben ser una lista de entre 2 y 50 elementos.',
      ),
    );
    return [];
  }

  const participants: Participant[] = [];
  const ids = new Set<string>();
  for (const [index, candidate] of value.entries()) {
    const path = `participants[${index}]`;
    if (!isRecord(candidate)) {
      issues.push(issue('E_VALIDATION_PARTICIPANTS', path, 'El participante debe ser un objeto.'));
      continue;
    }

    rejectUnknownFields(candidate, PARTICIPANT_KEYS, path, issues);
    const id = validateIdentifier(candidate.id, `${path}.id`, issues);
    const name = validateText(candidate.name, `${path}.name`, 100, issues);
    if (id !== undefined) {
      if (ids.has(id)) {
        issues.push(
          issue('E_VALIDATION_DUPLICATE_ID', `${path}.id`, 'El identificador está repetido.'),
        );
      }
      ids.add(id);
    }
    if (id !== undefined && name !== undefined) {
      participants.push({ id, name });
    }
  }
  return participants;
}

function validateExpenses(
  value: unknown,
  participantIds: ReadonlySet<string>,
  issues: DomainIssue[],
): Expense[] {
  if (!Array.isArray(value) || value.length < 1 || value.length > 500) {
    issues.push(
      issue(
        'E_VALIDATION_EXPENSES',
        'expenses',
        'Los gastos deben ser una lista de entre 1 y 500 elementos.',
      ),
    );
    return [];
  }

  const expenses: Expense[] = [];
  const ids = new Set<string>();
  for (const [index, candidate] of value.entries()) {
    const path = `expenses[${index}]`;
    if (!isRecord(candidate)) {
      issues.push(issue('E_VALIDATION_EXPENSES', path, 'El gasto debe ser un objeto.'));
      continue;
    }

    rejectUnknownFields(candidate, EXPENSE_KEYS, path, issues);
    const id = validateIdentifier(candidate.id, `${path}.id`, issues);
    const description = validateText(candidate.description, `${path}.description`, 200, issues);
    const amountMinor = validateAmount(candidate.amountMinor, `${path}.amountMinor`, issues);
    const paidBy = validateReference(candidate.paidBy, `${path}.paidBy`, participantIds, issues);
    const splitAmong = validateSplitAmong(
      candidate.splitAmong,
      `${path}.splitAmong`,
      participantIds,
      issues,
    );

    if (id !== undefined) {
      if (ids.has(id)) {
        issues.push(
          issue('E_VALIDATION_DUPLICATE_ID', `${path}.id`, 'El identificador está repetido.'),
        );
      }
      ids.add(id);
    }
    if (
      id !== undefined &&
      description !== undefined &&
      amountMinor !== undefined &&
      paidBy !== undefined &&
      splitAmong !== undefined
    ) {
      expenses.push({ id, description, amountMinor, paidBy, splitAmong });
    }
  }
  return expenses;
}

function validateIdentifier(
  value: unknown,
  path: string,
  issues: DomainIssue[],
): string | undefined {
  if (
    typeof value !== 'string' ||
    value.length < 1 ||
    value.length > 64 ||
    !PARTICIPANT_ID_PATTERN.test(value)
  ) {
    issues.push(
      issue('E_VALIDATION_TEXT', path, 'El identificador no tiene el formato permitido.'),
    );
    return undefined;
  }
  return value;
}

function validateText(
  value: unknown,
  path: string,
  maximumLength: number,
  issues: DomainIssue[],
): string | undefined {
  if (typeof value !== 'string' || value.trim().length < 1 || value.length > maximumLength) {
    issues.push(issue('E_VALIDATION_TEXT', path, 'El texto no cumple la longitud permitida.'));
    return undefined;
  }
  return value;
}

function validateAmount(value: unknown, path: string, issues: DomainIssue[]): number | undefined {
  if (typeof value !== 'number' || !Number.isSafeInteger(value) || value <= 0) {
    issues.push(
      issue('E_VALIDATION_AMOUNT', path, 'El importe debe ser un entero seguro positivo.'),
    );
    return undefined;
  }
  return value;
}

function validateReference(
  value: unknown,
  path: string,
  participantIds: ReadonlySet<string>,
  issues: DomainIssue[],
): string | undefined {
  if (typeof value !== 'string' || !participantIds.has(value)) {
    issues.push(
      issue('E_VALIDATION_UNKNOWN_PARTICIPANT', path, 'El participante referenciado no existe.'),
    );
    return undefined;
  }
  return value;
}

function validateSplitAmong(
  value: unknown,
  path: string,
  participantIds: ReadonlySet<string>,
  issues: DomainIssue[],
): string[] | undefined {
  if (!Array.isArray(value) || value.length < 1 || value.length > 50) {
    issues.push(issue('E_VALIDATION_SPLIT_AMONG', path, 'El reparto debe ser una lista no vacía.'));
    return undefined;
  }

  const splitAmong: string[] = [];
  const ids = new Set<string>();
  let hasInvalidEntry = false;
  for (const [index, candidate] of value.entries()) {
    const itemPath = `${path}[${index}]`;
    if (typeof candidate !== 'string') {
      issues.push(
        issue('E_VALIDATION_SPLIT_AMONG', itemPath, 'El reparto debe contener identificadores.'),
      );
      hasInvalidEntry = true;
      continue;
    }
    if (ids.has(candidate)) {
      issues.push(
        issue('E_VALIDATION_SPLIT_AMONG', itemPath, 'El reparto no puede repetir identificadores.'),
      );
      hasInvalidEntry = true;
    }
    ids.add(candidate);
    if (!participantIds.has(candidate)) {
      issues.push(
        issue(
          'E_VALIDATION_UNKNOWN_PARTICIPANT',
          itemPath,
          'El participante referenciado no existe.',
        ),
      );
      hasInvalidEntry = true;
    }
    splitAmong.push(candidate);
  }
  return hasInvalidEntry ? undefined : splitAmong;
}

function rejectUnknownFields(
  value: UnknownRecord,
  allowedKeys: readonly string[],
  path: string,
  issues: DomainIssue[],
): void {
  for (const key of Object.keys(value)) {
    if (!allowedKeys.includes(key)) {
      const fieldPath = path === '' ? key : `${path}.${key}`;
      issues.push(issue('E_VALIDATION_UNKNOWN_FIELD', fieldPath, 'El campo no está permitido.'));
    }
  }
}

function issue(code: DomainIssueCode, path: string, message: string): DomainIssue {
  return { code, path, message };
}

function isRecord(value: unknown): value is UnknownRecord {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function compareIssues(left: DomainIssue, right: DomainIssue): number {
  return compareText(left.path, right.path) || compareText(left.code, right.code);
}

function compareText(left: string, right: string): number {
  return left < right ? -1 : left > right ? 1 : 0;
}
