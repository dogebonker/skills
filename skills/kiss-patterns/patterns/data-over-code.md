# Data Over Code

When branches only map an input to a value, replace them with a table and a lookup.

Refs: http://www.catb.org/esr/writings/taoup/html/ch01s06.html
Example: [examples/data-over-code.py](../examples/data-over-code.py)

**Principle** — Eric Raymond's Rule of Representation (The Art of Unix Programming): fold knowledge into data so program logic can be simple and robust. A table is easier to read, review, test and change than a ladder of branches with the same shape. Rich Hickey's "Simple Made Easy" also lists rules and declarative data manipulation as simpler than conditionals.

**Violation signals** — `if/elif` or `switch` ladders where every branch returns a constant (`shipping_cents_v1`). Branches that differ only in literals. The same key checked in several functions, each returning a different attribute. Adding a case means adding code, not a row.

**Fix** — Put the mapping in a dict, `Map` or object literal (`SHIPPING_CENTS`) with a named default, and look it up (`SHIPPING_CENTS.get(country, DEFAULT_SHIPPING_CENTS)`). When each key has several attributes, map to a record. When entries need behaviour, map to functions. Load the table from config only if non-developers change it.

**When not to apply** — Branches with different logic, side effects or ordering rules are not a table. Two or three cases read fine as `if`. In TypeScript, a `switch` over a union with a `never` check gives exhaustiveness that a plain object lookup does not, unless you type it as `Record<Union, Value>`.

**Related** — **Strategy** (`gof-patterns-typescript/patterns/strategy.md`) for a table of functions; **State** (`gof-patterns-typescript/patterns/state.md`) for transition tables; [`rule-of-least-power`](rule-of-least-power.md); [`magic-values`](../../dry-patterns/patterns/magic-values.md); **OCP** (`solid-patterns-typescript/patterns/ocp.md`).
