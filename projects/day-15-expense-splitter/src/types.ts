export const CONTRACT_VERSION = 'v1' as const;

export interface Participant {
  readonly id: string;
  readonly name: string;
}

export interface Expense {
  readonly id: string;
  readonly description: string;
  readonly amountMinor: number;
  readonly paidBy: string;
  readonly splitAmong: readonly string[];
}

export interface ExpenseDocument {
  readonly version: typeof CONTRACT_VERSION;
  readonly currency: string;
  readonly participants: readonly Participant[];
  readonly expenses: readonly Expense[];
}

export interface Balance {
  readonly participantId: string;
  readonly name: string;
  readonly paidMinor: number;
  readonly owedMinor: number;
  readonly balanceMinor: number;
}

export interface Transfer {
  readonly from: string;
  readonly to: string;
  readonly amountMinor: number;
}

export interface ExpenseSplitResult {
  readonly version: typeof CONTRACT_VERSION;
  readonly currency: string;
  readonly totalMinor: number;
  readonly balances: readonly Balance[];
  readonly transfers: readonly Transfer[];
}

export type DomainIssueCode =
  | 'E_VALIDATION_ROOT'
  | 'E_VALIDATION_UNKNOWN_FIELD'
  | 'E_VALIDATION_VERSION'
  | 'E_VALIDATION_CURRENCY'
  | 'E_VALIDATION_PARTICIPANTS'
  | 'E_VALIDATION_EXPENSES'
  | 'E_VALIDATION_DUPLICATE_ID'
  | 'E_VALIDATION_TEXT'
  | 'E_VALIDATION_AMOUNT'
  | 'E_VALIDATION_UNKNOWN_PARTICIPANT'
  | 'E_VALIDATION_SPLIT_AMONG';

export interface DomainIssue {
  readonly code: DomainIssueCode;
  readonly path: string;
  readonly message: string;
}
