# Interface Segregation (ISP)

A client should depend only on the members it actually uses.

Refs: https://cs.utexas.edu/~downing/papers/ISP-1996.pdf
Example: [examples/isp.ts](../examples/isp.ts)

**Principle** — Martin calls large interfaces that serve several kinds of clients "fat" and shows that they couple those clients to each other. Clients should see small, cohesive interfaces instead. TypeScript's structural typing makes this cheap: the consumer can name the slice it needs, and any object with those members satisfies it with no `implements` clause.

**Violation signals** — A function takes a whole store or service (`welcomeMessageV1(store: CustomerStore)`) and calls one method. Test fakes full of stubs that throw "not used". Implementations with methods that throw "not supported". Changes to an unrelated method force recompiles or new fakes.

**Fix** — Type the parameter as the slice: `type EmailLookup = Pick<CustomerStore, "findEmail">`, or a small interface declared next to the consumer. `InMemoryCustomerStore` still satisfies it, and the test passes the literal `{ findEmail: () => "..." }`.

**When not to apply** — Do not create one interface per method across the codebase, or split an interface that every client uses whole. A `Pick` at the call site is lighter than a family of named role interfaces nobody else reuses.

**Related** — **Adapter** (`gof-patterns-typescript/patterns/adapter.md`) to present a narrow interface over a wide object; **Facade** (`gof-patterns-typescript/patterns/facade.md`) for one narrow entry over many; **SRP** ([srp.md](srp.md)) for the same split applied to modules; **DIP** ([dip.md](dip.md)), whose ports should be this small; **Pattern overuse** (`kiss-patterns/patterns/pattern-overuse.md`).
