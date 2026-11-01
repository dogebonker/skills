export {};

// Chain of Responsibility: each handler either answers or passes the request to the next one.
interface ExpenseRequest {
  readonly employee: string;
  readonly amount: number;
}

interface Approver {
  setNext(next: Approver): Approver;
  approve(req: ExpenseRequest): string;
}

class LimitApprover implements Approver {
  #next?: Approver;
  readonly #role: string;
  readonly #limit: number;

  constructor(role: string, limit: number) {
    this.#role = role;
    this.#limit = limit;
  }

  setNext(next: Approver): Approver {
    this.#next = next;
    return next;
  }

  approve(req: ExpenseRequest): string {
    if (req.amount <= this.#limit) return `${this.#role} approved ${req.amount} for ${req.employee}`;
    return this.#next?.approve(req) ?? `nobody can approve ${req.amount}`;
  }
}

class ValidAmount implements Approver {
  #next?: Approver;

  setNext(next: Approver): Approver {
    this.#next = next;
    return next;
  }

  approve(req: ExpenseRequest): string {
    if (!(req.amount > 0)) return `rejected invalid amount ${req.amount}`;
    return this.#next?.approve(req) ?? "no handler";
  }
}

const approvers = new ValidAmount();
approvers
  .setNext(new LimitApprover("manager", 500))
  .setNext(new LimitApprover("director", 5000))
  .setNext(new LimitApprover("cfo", 50000));

for (const amount of [-5, 120, 2400, 30000, 90000]) {
  console.log(approvers.approve({ employee: "grace", amount }));
}
