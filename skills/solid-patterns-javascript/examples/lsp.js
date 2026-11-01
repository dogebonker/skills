'use strict';

// LSP: a subtype must keep the promises callers rely on. Checking accounts pay the same in both.

// --- Violation: FixedDepositAccountV1 extends AccountV1 but throws where AccountV1 promised to withdraw.
class AccountV1 {
  constructor(balanceCents) {
    this.balanceCents = balanceCents;
  }

  withdraw(cents) {
    if (cents > this.balanceCents) throw new Error('insufficient funds');
    this.balanceCents -= cents;
  }
}

class FixedDepositAccountV1 extends AccountV1 {
  withdraw() {
    throw new Error('fixed deposit: withdrawals locked');
  }
}

const payInvoiceV1 = (from, cents) => {
  from.withdraw(cents);
  return `paid ${cents}, left ${from.balanceCents}`;
};

// --- Fix: no shared base. Only objects that can keep the withdraw contract have withdraw.
class CheckingAccount {
  #balanceCents;

  constructor(balanceCents) {
    this.#balanceCents = balanceCents;
  }

  get balanceCents() {
    return this.#balanceCents;
  }

  withdraw(cents) {
    if (cents > this.#balanceCents) throw new Error('insufficient funds');
    this.#balanceCents -= cents;
  }
}

class FixedDeposit {
  #balanceCents;

  constructor(balanceCents) {
    this.#balanceCents = balanceCents;
  }

  get balanceCents() {
    return this.#balanceCents;
  }
}

// Duck typing: the capability is the method, checked once where sources are chosen.
const canWithdraw = (account) => typeof account.withdraw === 'function';

const payFrom = (from, cents) => {
  from.withdraw(cents);
  return `paid ${cents}, left ${from.balanceCents}`;
};

module.exports = { AccountV1, FixedDepositAccountV1, payInvoiceV1, CheckingAccount, FixedDeposit, canWithdraw, payFrom };

if (require.main === module) {
  console.log('violation, checking:', payInvoiceV1(new AccountV1(50000), 1000));
  console.log('fix, checking:      ', payFrom(new CheckingAccount(50000), 1000));
  console.log('same output:', JSON.stringify(payInvoiceV1(new AccountV1(50000), 1000)) === JSON.stringify(payFrom(new CheckingAccount(50000), 1000)));
  try {
    payInvoiceV1(new FixedDepositAccountV1(50000), 1000);
  } catch (e) {
    console.log('violation, fixed deposit throws:', e.message);
  }
  const sources = [new FixedDeposit(50000), new CheckingAccount(20000)].filter(canWithdraw);
  console.log('fix, payable sources:', sources.map((a) => a.constructor.name));
}
