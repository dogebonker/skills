# Wrong Abstraction

When a shared function has grown a flag and a branch per caller, inline it back into the callers and start again.

Refs: https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction
Example: [examples/wrong-abstraction.ts](../examples/wrong-abstraction.ts)

**Principle** — Sandi Metz: duplication is cheaper than the wrong abstraction. The sequence she describes: someone extracts shared code, a new need almost fits, a parameter and conditional are added, and repeated edits leave one function serving loosely related cases. Sunk cost keeps it alive. Kent C. Dodds' AHA ("avoid hasty abstractions", a name he credits to Cher Scarlett) gives the same advice: duplicate until the shape of the variation is clear.

**Violation signals** — Boolean or mode parameters that only one caller passes (`forInvoice`, `forEmail`). Conditionals that combine flags (`roundToWhole && !forInvoice`). Callers that pass options to switch off behaviour. A change for one caller breaks another.

**Fix** — Follow Metz's steps: inline the abstraction into every caller, keep in each caller only the branch its arguments select, and delete the rest. `formatPrice(cents, opts)` becomes `invoiceTotal`, `emailPrice` and `bannerPrice`, each a line long. Re-extract later only if real shared knowledge remains.

**When not to apply** — An abstraction with stable callers and no caller-specific flags is fine. Do not inline a well-used library function just because one caller needs an extra option; wrap it in that caller.

**Related** — **Strategy** (`gof-patterns-typescript/patterns/strategy.md`) when real variation remains and a passed-in function replaces the flags; [`rule-of-three`](rule-of-three.md); [`speculative-generality`](../../kiss-patterns/patterns/speculative-generality.md); **SRP** (`solid-patterns-typescript/patterns/srp.md`); **OCP** (`solid-patterns-typescript/patterns/ocp.md`).
