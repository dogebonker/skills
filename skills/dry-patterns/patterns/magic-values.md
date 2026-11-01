# Magic Values

Replace unexplained literals with named constants or enums so the meaning and the single place to change it are visible.

Refs: https://refactoring.guru/replace-magic-number-with-symbolic-constant
Example: [examples/magic-values.py](../examples/magic-values.py)

**Principle** — A literal like `5000`, `3` or `259200` carries a business decision with no name. Readers must guess it, and changing it means finding every copy without hitting the same number used for something else. A named constant documents the value and gives it one definition.

**Violation signals** — Numeric or string literals in conditions (`status == 3`, `subtotal >= 5000`). Durations in raw seconds or milliseconds. Status strings compared in several files. The same literal repeated in code and tests.

**Fix** — Name the knowledge: `FREE_SHIPPING_THRESHOLD_CENTS`, `STANDARD_SHIPPING_CENTS`, `PAYMENT_REMINDER_DAYS * SECONDS_PER_DAY`. Codes that select behaviour become an `Enum` (`OrderStatus.CANCELLED`) in Python or a string-literal union in TypeScript. refactoring.guru notes that numbers encoding a type can go further, with Replace Type Code with Class, Subclasses or State/Strategy. Use `len()` or `.length` instead of literal sizes.

**When not to apply** — Obvious values stay inline: `0`, `1`, `i + 1`, `/ 100` for cents to euros, `24 * 60 * 60` written out. A constant named after its value (`TWENTY = 20`) adds nothing. Do not move a constant to a shared module when only one function reads it.

**Related** — **State** (`gof-patterns-typescript/patterns/state.md`) when a status code drives behaviour; [`single-source-of-truth`](single-source-of-truth.md); [`knowledge-not-text`](knowledge-not-text.md) for constants that match by coincidence; [`data-over-code`](../../kiss-patterns/patterns/data-over-code.md) for tables of named values.
