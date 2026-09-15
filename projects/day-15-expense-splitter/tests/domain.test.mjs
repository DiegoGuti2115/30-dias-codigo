import assert from 'node:assert/strict';
import test from 'node:test';

import { splitExpenses } from '../dist/expense-splitter.js';
import { DomainValidationError } from '../dist/validation.js';

function documentFor(expenses, participants = defaultParticipants()) {
  return { version: 'v1', currency: 'EUR', participants, expenses };
}

function defaultParticipants() {
  return [
    { id: 'ana', name: 'Ana' },
    { id: 'bruno', name: 'Bruno' },
    { id: 'carla', name: 'Carla' },
  ];
}

function expense(overrides = {}) {
  return {
    id: 'expense-1',
    description: 'Gasto sintético',
    amountMinor: 100,
    paidBy: 'ana',
    splitAmong: ['ana', 'bruno'],
    ...overrides,
  };
}

function validationCodes(input) {
  assert.throws(
    () => splitExpenses(input),
    (error) => {
      assert.ok(error instanceof DomainValidationError);
      return true;
    },
  );

  try {
    splitExpenses(input);
  } catch (error) {
    return error.issues.map((issue) => issue.code);
  }
  throw new Error('Se esperaba un error de validación.');
}

test('implements exact splits, declared remainder order, and payer exclusion', () => {
  const exact = splitExpenses(documentFor([expense()]));
  assert.deepEqual(exact.transfers, [{ from: 'bruno', to: 'ana', amountMinor: 50 }]);

  const remainder = splitExpenses(
    documentFor([
      expense({
        amountMinor: 5,
        splitAmong: ['carla', 'bruno', 'ana'],
      }),
    ]),
  );
  assert.deepEqual(remainder.balances, [
    { participantId: 'ana', name: 'Ana', paidMinor: 5, owedMinor: 1, balanceMinor: 4 },
    { participantId: 'bruno', name: 'Bruno', paidMinor: 0, owedMinor: 2, balanceMinor: -2 },
    { participantId: 'carla', name: 'Carla', paidMinor: 0, owedMinor: 2, balanceMinor: -2 },
  ]);

  const payerOutsideSplit = splitExpenses(
    documentFor([expense({ amountMinor: 300, splitAmong: ['bruno'] })]),
  );
  assert.deepEqual(payerOutsideSplit.transfers, [{ from: 'bruno', to: 'ana', amountMinor: 300 }]);
});

test('accumulates balances and produces deterministic settlement order', () => {
  const result = splitExpenses(
    documentFor([
      expense({ id: 'first', amountMinor: 900, splitAmong: ['ana', 'bruno', 'carla'] }),
      expense({
        id: 'second',
        amountMinor: 300,
        paidBy: 'bruno',
        splitAmong: ['bruno', 'carla'],
      }),
    ]),
  );

  assert.deepEqual(
    result.balances.map(({ participantId, balanceMinor }) => ({ participantId, balanceMinor })),
    [
      { participantId: 'ana', balanceMinor: 600 },
      { participantId: 'bruno', balanceMinor: -150 },
      { participantId: 'carla', balanceMinor: -450 },
    ],
  );
  assert.deepEqual(result.transfers, [
    { from: 'bruno', to: 'ana', amountMinor: 150 },
    { from: 'carla', to: 'ana', amountMinor: 450 },
  ]);

  const balanced = splitExpenses(
    documentFor([
      expense({ id: 'ana-paid', amountMinor: 200 }),
      expense({ id: 'bruno-paid', amountMinor: 200, paidBy: 'bruno' }),
    ]),
  );
  assert.deepEqual(balanced.transfers, []);
  assert.deepEqual(
    balanced.balances.map((balance) => balance.balanceMinor),
    [0, 0, 0],
  );

  const multiCreditor = splitExpenses(
    documentFor(
      [
        expense({ id: 'ana-paid', amountMinor: 500, splitAmong: ['carla'] }),
        expense({ id: 'bruno-paid', amountMinor: 200, paidBy: 'bruno', splitAmong: ['david'] }),
        expense({ id: 'carla-paid', amountMinor: 200, paidBy: 'carla', splitAmong: ['david'] }),
      ],
      [
        { id: 'ana', name: 'Ana' },
        { id: 'bruno', name: 'Bruno' },
        { id: 'carla', name: 'Carla' },
        { id: 'david', name: 'David' },
      ],
    ),
  );
  assert.deepEqual(multiCreditor.transfers, [
    { from: 'carla', to: 'ana', amountMinor: 300 },
    { from: 'david', to: 'ana', amountMinor: 200 },
    { from: 'david', to: 'bruno', amountMinor: 200 },
  ]);
});

test('preserves currency and monetary conservation for every result', () => {
  const result = splitExpenses(
    documentFor(
      [expense({ amountMinor: 1, splitAmong: ['ana', 'bruno'] })],
      [
        { id: 'ana', name: 'Persona repetida' },
        { id: 'bruno', name: 'Persona repetida' },
      ],
    ),
  );
  const repeat = splitExpenses(
    documentFor(
      [expense({ amountMinor: 1, splitAmong: ['ana', 'bruno'] })],
      [
        { id: 'ana', name: 'Persona repetida' },
        { id: 'bruno', name: 'Persona repetida' },
      ],
    ),
  );

  assert.equal(result.currency, 'EUR');
  assert.deepEqual(result, repeat);
  assert.equal(
    result.balances.reduce((sum, balance) => sum + balance.balanceMinor, 0),
    0,
  );
  const settledBalances = new Map(
    result.balances.map(({ participantId, balanceMinor }) => [participantId, balanceMinor]),
  );
  for (const transfer of result.transfers) {
    settledBalances.set(transfer.from, settledBalances.get(transfer.from) + transfer.amountMinor);
    settledBalances.set(transfer.to, settledBalances.get(transfer.to) - transfer.amountMinor);
  }
  assert.deepEqual([...settledBalances.values()], [0, 0]);
});

test('rejects documented invalid document categories with ordered issues', () => {
  const valid = documentFor([expense()]);
  const cases = [
    [{}, 'E_VALIDATION_ROOT'],
    [{ ...valid, version: 'v2' }, 'E_VALIDATION_VERSION'],
    [{ ...valid, currency: 'eur' }, 'E_VALIDATION_CURRENCY'],
    [{ ...valid, participants: [{ id: 'ana', name: 'Ana' }] }, 'E_VALIDATION_PARTICIPANTS'],
    [{ ...valid, expenses: [] }, 'E_VALIDATION_EXPENSES'],
    [
      { ...valid, participants: [valid.participants[0], valid.participants[0]] },
      'E_VALIDATION_DUPLICATE_ID',
    ],
    [documentFor([expense({ description: '   ' })]), 'E_VALIDATION_TEXT'],
    [documentFor([expense({ amountMinor: 0 })]), 'E_VALIDATION_AMOUNT'],
    [documentFor([expense({ paidBy: 'nadie' })]), 'E_VALIDATION_UNKNOWN_PARTICIPANT'],
    [documentFor([expense({ splitAmong: ['ana', 'ana'] })]), 'E_VALIDATION_SPLIT_AMONG'],
    [{ ...valid, extra: true }, 'E_VALIDATION_UNKNOWN_FIELD'],
  ];

  for (const [input, expectedCode] of cases) {
    assert.ok(validationCodes(input).includes(expectedCode));
  }

  const issues = validationCodes({
    version: 'v2',
    currency: 'eur',
    participants: [],
    expenses: [],
  });
  assert.deepEqual(issues, [...issues].sort());
});
