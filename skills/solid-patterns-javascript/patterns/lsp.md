# Liskov Substitution (LSP)

Any object passed where a contract is expected must keep every promise callers rely on.

Refs: https://www.cs.columbia.edu/~wing/publications/LiskovWing94.pdf
Example: [examples/lsp.js](../examples/lsp.js)

**Principle** — Liskov and Wing define a subtype by behaviour: it may accept more and promise more, and it must keep the supertype's invariants. Martin's 1996 paper (https://cs.utexas.edu/~downing/papers/LSP-1996.pdf) adds that a subclass throwing where the base did not breaks clients that do not expect the exception. JavaScript has no declared types, so with duck typing the contract is whatever callers depend on: method names, argument handling, return shape, thrown errors. It applies to plain objects as much as to `extends`.

**Violation signals** — An override that throws "not supported" or does nothing (`FixedDepositAccountV1.withdraw`). Callers branching on `instanceof` or `constructor.name`. An implementation that returns a Promise where the others return values, or `null` where others throw.

**Fix** — Drop the shared base and give the method only to objects that can keep its contract: `CheckingAccount` has `withdraw`, `FixedDeposit` does not. `canWithdraw` checks the capability once, where payment sources are chosen, and `payFrom` trusts its argument.

**When not to apply** — Do not build class hierarchies just to have something to substitute. Plain objects and one capability check are often enough, and a JSDoc `@typedef` or a TypeScript check can state the contract more cheaply than runtime guards everywhere.

**Related** — **Template Method** (`gof-patterns-javascript/patterns/template-method.md`), whose subclasses must honour each step; **Adapter** (`gof-patterns-javascript/patterns/adapter.md`) to wrap an object instead of subclassing it; **ISP** ([isp.md](isp.md)) for the capability split; **OCP** ([ocp.md](ocp.md)).
