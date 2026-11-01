# Parallel Hierarchies

When every new subclass in one hierarchy forces a matching subclass in another, fold one hierarchy into the other.

Refs: https://refactoring.guru/smells/parallel-inheritance-hierarchies
Example: [examples/parallel-hierarchies.ts](../examples/parallel-hierarchies.ts)

**Principle** — Two class trees that grow in lockstep encode one piece of knowledge twice: "an SMS exists" is stated by `LegacySms` and again by `SmsFormatter`. refactoring.guru files it under change preventers.

**Violation signals** — Name pairs such as `Email`/`EmailFormatter`, `Invoice`/`InvoiceRenderer`, `Order`/`OrderDto`/`OrderMapper`. A factory that picks the partner with `instanceof` (`formatterFor`). Casts from the base type to the matching subtype inside the partner (`n as LegacyEmail`). Adding a variant needs edits in two or more trees.

**Fix** — Make instances of one hierarchy refer to the other, then move methods and fields with Move Method and Move Field until one tree is empty, and delete it. In the example `format()` moves onto `EmailNotification` and `SmsNotification`, and the formatter tree, the factory and the casts disappear. With a closed set of variants, a discriminated union and one `switch` is the smaller alternative.

**When not to apply** — Keep the second tree when the two dimensions really vary independently (any channel times any template), or when the second tree must live in a different layer, such as persistence mappers kept out of the domain. refactoring.guru also says to revert if the merge makes the design worse.

**Related** — **Bridge** (`gof-patterns-typescript/patterns/bridge.md`) for two independent dimensions; **Visitor** (`gof-patterns-typescript/patterns/visitor.md`) when operations must stay outside the node classes; **SRP** (`solid-patterns-typescript/patterns/srp.md`); [`knowledge-not-text`](knowledge-not-text.md).
