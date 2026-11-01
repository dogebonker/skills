export {};

// LSP: a subtype must keep the promises callers rely on. Checking accounts pay the same in both.

// --- Violation: FixedDepositAccountV1 is an AccountV1 but throws where AccountV1 promised to withdraw.
class AccountV1 {
  protected balanceCents: number;

  constructor(balanceCents: number) {
    this.balanceCents = balanceCents;
  }

  get balance(): number {
    return this.balanceCents;
  }

  withdraw(cents: number): void {
    if (cents > this.balanceCents) throw new Error("insufficient funds");
    this.balanceCents -= cents;
  }
}

class FixedDepositAccountV1 extends AccountV1 {
  override withdraw(_cents: number): void {
    throw new Error("fixed deposit: withdrawals locked");
  }
}

function payInvoiceV1(from: AccountV1, cents: number): string {
  from.withdraw(cents);
  return `paid ${cents}, left ${from.balance}`;
}

// --- Fix: split the capability. Only types that can keep the withdraw contract claim it.
interface HasBalance {
  readonly balance: number;
}

interface Withdrawable extends HasBalance {
  withdraw(cents: number): void;
}

class CheckingAccount implements Withdrawable {
  #balanceCents: number;

  constructor(balanceCents: number) {
    this.#balanceCents = balanceCents;
  }

  get balance(): number {
    return this.#balanceCents;
  }

  withdraw(cents: number): void {
    if (cents > this.#balanceCents) throw new Error("insufficient funds");
    this.#balanceCents -= cents;
  }
}

class FixedDeposit implements HasBalance {
  readonly balance: number;

  constructor(balanceCents: number) {
    this.balance = balanceCents;
  }
}

function payFrom(from: Withdrawable, cents: number): string {
  from.withdraw(cents);
  return `paid ${cents}, left ${from.balance}`;
}

// Never called: documents that the compiler now rejects the bad substitution.
function rejectedAtCompileTime(): void {
  // @ts-expect-error FixedDeposit has no withdraw, so it is not a Withdrawable.
  payFrom(new FixedDeposit(50000), 1000);
}
void rejectedAtCompileTime;

console.log("violation, checking:", payInvoiceV1(new AccountV1(50000), 1000));
console.log("fix, checking:      ", payFrom(new CheckingAccount(50000), 1000));
console.log("same output:", JSON.stringify(payInvoiceV1(new AccountV1(50000), 1000)) === JSON.stringify(payFrom(new CheckingAccount(50000), 1000)));
try {
  payInvoiceV1(new FixedDepositAccountV1(50000), 1000);
} catch (e) {
  console.log("violation, fixed deposit throws at runtime:", (e as Error).message);
}
console.log("fix, fixed deposit: not a Withdrawable, rejected by tsc; balance", new FixedDeposit(50000).balance);
