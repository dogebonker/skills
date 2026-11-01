# Single Source of Truth

Keep each list, constant, schema or setting in one place and derive every other use from it.

Refs: https://en.wikipedia.org/wiki/Single_source_of_truth
Example: [examples/single-source-of-truth.ts](../examples/single-source-of-truth.ts)

**Principle** — A data element is edited in exactly one place. Other code references or derives from that master instead of holding its own copy, so copies cannot drift. In code this means types, validators, UI options and docs come from one declaration.

**Violation signals** — An enum-like list repeated as a union type, an array for a dropdown and an `if a || b || c` check. A config value duplicated in code, `.env.example` and docs. A database column list mirrored by hand in a DTO. Comments such as "keep in sync with X".

**Fix** — Declare the data once and derive the rest. In TypeScript, `const ORDER_STATUSES = [...] as const` gives `type OrderStatus = (typeof ORDER_STATUSES)[number]`, the dropdown and `isOrderStatus()`. In Python, an `Enum` or a module-level tuple plays the same role, and `typing.get_args` or iteration derives the rest.

**When not to apply** — Two services owned by different teams may each keep a copy at a published contract boundary; there, version the contract instead of sharing internals. Do not build a central "constants" module for values with one user: keep the value beside its only reader.

**Related** — **Observer** (`gof-patterns-typescript/patterns/observer.md`) when a derived copy must stay in sync at runtime; [`magic-values`](magic-values.md) for naming the value; [`generate-dont-repeat`](generate-dont-repeat.md) when derivation needs a build step; [`duplicated-logic-across-layers`](duplicated-logic-across-layers.md) for client and server copies.
