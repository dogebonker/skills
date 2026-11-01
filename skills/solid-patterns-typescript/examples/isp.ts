export {};

// ISP: a client depends only on the members it calls. Both versions build the same message.

type Customer = { id: string; email: string; overdue: boolean };

interface CustomerStore {
  findEmail(id: string): string | undefined;
  save(c: Customer): void;
  remove(id: string): void;
  listOverdue(): Customer[];
  exportCsv(): string;
}

class InMemoryCustomerStore implements CustomerStore {
  readonly #rows = new Map<string, Customer>();

  findEmail(id: string): string | undefined {
    return this.#rows.get(id)?.email;
  }
  save(c: Customer): void {
    this.#rows.set(c.id, c);
  }
  remove(id: string): void {
    this.#rows.delete(id);
  }
  listOverdue(): Customer[] {
    return [...this.#rows.values()].filter((c) => c.overdue);
  }
  exportCsv(): string {
    return [...this.#rows.values()].map((c) => `${c.id},${c.email}`).join("\n");
  }
}

// --- Violation: needs one method but demands all five, so every caller and fake carries them.
function welcomeMessageV1(store: CustomerStore, id: string): string {
  const email = store.findEmail(id);
  if (!email) throw new Error(`no customer ${id}`);
  return `Welcome! Receipts go to ${email}.`;
}

// --- Fix: name the slice this client uses. Structural typing lets any object with findEmail fit.
type EmailLookup = Pick<CustomerStore, "findEmail">;

function welcomeMessage(store: EmailLookup, id: string): string {
  const email = store.findEmail(id);
  if (!email) throw new Error(`no customer ${id}`);
  return `Welcome! Receipts go to ${email}.`;
}

const store = new InMemoryCustomerStore();
store.save({ id: "c-7", email: "ana@example.com", overdue: false });
console.log("violation:", welcomeMessageV1(store, "c-7"));
console.log("fix:      ", welcomeMessage(store, "c-7"));

// The cost shows in tests: the fat version needs four unused stubs, the fix needs a one-line literal.
const unused = (): never => {
  throw new Error("not used by welcomeMessage");
};
const fatFake: CustomerStore = {
  findEmail: () => "test@example.com",
  save: unused,
  remove: unused,
  listOverdue: unused,
  exportCsv: unused,
};
console.log("violation fake:", welcomeMessageV1(fatFake, "x"));
console.log("fix fake:      ", welcomeMessage({ findEmail: () => "test@example.com" }, "x"));
console.log("same output:", welcomeMessageV1(fatFake, "x") === welcomeMessage({ findEmail: () => "test@example.com" }, "x"));
