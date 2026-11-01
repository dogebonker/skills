# Liskov Substitution (LSP)

Any value that claims a type must keep every promise callers of that type rely on.

Refs: https://www.cs.columbia.edu/~wing/publications/LiskovWing94.pdf
Example: [examples/lsp.ts](../examples/lsp.ts)

**Principle** — Liskov and Wing define a subtype by behaviour: it may accept more (weaker preconditions) and promise more (stronger postconditions), and it must keep the supertype's invariants. Martin's 1996 paper (https://cs.utexas.edu/~downing/papers/LSP-1996.pdf) adds that a subclass throwing where the base did not breaks clients that do not expect the exception. TypeScript checks shape, not behaviour, so it accepts these violations.

**Violation signals** — An override that throws "not supported" or is empty (`FixedDepositAccountV1.withdraw`). Callers using `instanceof` to avoid one subtype. An override that narrows a parameter: method shorthand (`handle(e: Event)`) stays bivariant even under `strictFunctionTypes`, so tsc lets it through.

**Fix** — Split the capability so that only types able to keep the contract claim it: `HasBalance` and `Withdrawable`. `FixedDeposit` implements only `HasBalance`, and `payFrom(new FixedDeposit(...))` becomes a compile error, pinned by `@ts-expect-error`. Write callback members as properties (`handle: (e: Event) => void`) to get contravariant checks.

**When not to apply** — Do not invent hierarchies to satisfy LSP. If two types share no contract, give them no common type. A union plus a narrowing check is often simpler than a capability lattice.

**Related** — **Template Method** (`gof-patterns-typescript/patterns/template-method.md`) whose steps every subclass must honour; **Adapter** (`gof-patterns-typescript/patterns/adapter.md`) to wrap a type instead of subclassing it; **ISP** ([isp.md](isp.md)) for the split; **OCP** ([ocp.md](ocp.md)) depends on substitutable extensions.
