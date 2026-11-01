# Flat Over Nested

Handle special cases first with guard clauses that return, so the normal path reads last at one indentation level.

Refs: https://refactoring.guru/replace-nested-conditional-with-guard-clauses
Example: [examples/flat-over-nested.ts](../examples/flat-over-nested.ts)

**Principle** — Nested conditionals hide the normal flow: the reader has to keep every enclosing condition in mind to know when a line runs. Guard clauses turn the nesting into a flat list of checks, each ending the function, followed by the main logic. The Zen of Python states the same preference: flat is better than nested.

**Violation signals** — Arrow-shaped code with four or more indentation levels (`refundCentsV1`). A result variable assigned in many branches and returned at the end. `else` blocks far from their `if`. Loops nested in loops nested in `try`.

**Fix** — Follow refactoring.guru's steps: separate side effects from checks, move each check that returns or throws to the top, and merge guards with the same result using Consolidate Conditional Expression. `refundCents()` returns early for cancelled, unpaid, too-late and gift orders and ends with the normal refund. In loops, use `continue` for skips, and extract inner loops into named functions.

**When not to apply** — Guards suit preconditions and special cases. When two branches are equal, normal paths (an `if/else` choosing between two pricing rules), a plain `if/else` shows that symmetry better. Many guards in one function can signal a missing type or a table.

**Related** — **Chain of Responsibility** (`gof-patterns-typescript/patterns/chain-of-responsibility.md`) when guards become independent handlers; **State** (`gof-patterns-typescript/patterns/state.md`) when the nesting tests a status; [`data-over-code`](data-over-code.md); [`smallest-thing-that-works`](smallest-thing-that-works.md).
