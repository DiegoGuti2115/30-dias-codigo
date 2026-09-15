import {
  type Balance,
  CONTRACT_VERSION,
  type ExpenseDocument,
  type ExpenseSplitResult,
  type Transfer,
} from './types.js';
import { validateExpenseDocument } from './validation.js';

interface LedgerEntry {
  paidMinor: number;
  owedMinor: number;
  name: string;
}

interface SettlementPosition {
  participantId: string;
  remainingMinor: number;
}

export function splitExpenses(input: unknown): ExpenseSplitResult {
  const document = validateExpenseDocument(input);
  const ledger = createLedger(document);
  let totalMinor = 0;

  for (const expense of document.expenses) {
    totalMinor = addSafe(totalMinor, expense.amountMinor);
    const payer = ledger.get(expense.paidBy);
    if (payer === undefined) {
      throw new Error('El documento validado contiene un pagador desconocido.');
    }
    payer.paidMinor = addSafe(payer.paidMinor, expense.amountMinor);
    allocateExpense(expense, ledger);
  }

  const balances = [...ledger.entries()]
    .map(([participantId, entry]): Balance => {
      const balanceMinor = entry.paidMinor - entry.owedMinor;
      if (!Number.isSafeInteger(balanceMinor)) {
        throw new Error('El balance excede el rango seguro.');
      }
      return {
        participantId,
        name: entry.name,
        paidMinor: entry.paidMinor,
        owedMinor: entry.owedMinor,
        balanceMinor,
      };
    })
    .sort((left, right) => compareParticipantIds(left.participantId, right.participantId));

  const transfers = settleBalances(balances);
  return {
    version: CONTRACT_VERSION,
    currency: document.currency,
    totalMinor,
    balances,
    transfers,
  };
}

function createLedger(document: ExpenseDocument): Map<string, LedgerEntry> {
  return new Map(
    document.participants.map((participant) => [
      participant.id,
      { name: participant.name, paidMinor: 0, owedMinor: 0 },
    ]),
  );
}

function allocateExpense(
  expense: ExpenseDocument['expenses'][number],
  ledger: Map<string, LedgerEntry>,
): void {
  const baseShare = Math.floor(expense.amountMinor / expense.splitAmong.length);
  const remainder = expense.amountMinor % expense.splitAmong.length;

  for (const [index, participantId] of expense.splitAmong.entries()) {
    const participant = ledger.get(participantId);
    if (participant === undefined) {
      throw new Error('El documento validado contiene un participante de reparto desconocido.');
    }
    const share = baseShare + (index < remainder ? 1 : 0);
    participant.owedMinor = addSafe(participant.owedMinor, share);
  }
}

function settleBalances(balances: readonly Balance[]): Transfer[] {
  const debtors: SettlementPosition[] = balances
    .filter((balance) => balance.balanceMinor < 0)
    .map((balance) => ({
      participantId: balance.participantId,
      remainingMinor: -balance.balanceMinor,
    }));
  const creditors: SettlementPosition[] = balances
    .filter((balance) => balance.balanceMinor > 0)
    .map((balance) => ({
      participantId: balance.participantId,
      remainingMinor: balance.balanceMinor,
    }));
  const transfers: Transfer[] = [];
  let debtorIndex = 0;
  let creditorIndex = 0;

  while (debtorIndex < debtors.length && creditorIndex < creditors.length) {
    const debtor = debtors[debtorIndex];
    const creditor = creditors[creditorIndex];
    if (debtor === undefined || creditor === undefined) {
      throw new Error('No se pudo construir la liquidación.');
    }

    const amountMinor = Math.min(debtor.remainingMinor, creditor.remainingMinor);
    transfers.push({ from: debtor.participantId, to: creditor.participantId, amountMinor });
    debtor.remainingMinor -= amountMinor;
    creditor.remainingMinor -= amountMinor;

    if (debtor.remainingMinor === 0) {
      debtorIndex += 1;
    }
    if (creditor.remainingMinor === 0) {
      creditorIndex += 1;
    }
  }

  if (debtorIndex !== debtors.length || creditorIndex !== creditors.length) {
    throw new Error('Los balances no se pueden liquidar exactamente.');
  }
  return transfers;
}

function compareParticipantIds(left: string, right: string): number {
  return left < right ? -1 : left > right ? 1 : 0;
}

function addSafe(left: number, right: number): number {
  const sum = left + right;
  if (!Number.isSafeInteger(sum)) {
    throw new Error('El cálculo excede el rango seguro.');
  }
  return sum;
}
