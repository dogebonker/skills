# YAGNI

Build what today's requirement needs, and add a capability when a real need for it arrives.

Refs: https://martinfowler.com/bliki/Yagni.html
Example: [examples/yagni.ts](../examples/yagni.ts)

**Principle** — "You aren't gonna need it" comes from Extreme Programming. Fowler's bliki lists four costs of a presumptive feature: building it, delaying the features that matter, carrying its complexity through every later change, and repairing it when the real need turns out different. YAGNI depends on malleable code: tests and refactoring keep the later change cheap. Refactoring and other work that makes code easier to change are not YAGNI violations.

**Violation signals** — Types and parameters for cases the product does not support (`Money { amount, currency }` and `convert()` in a euro-only shop). Options and config keys every caller leaves at the default. Branches commented "for when we support X". A `version` field nothing reads.

**Fix** — Model the requirement as stated: `cartTotalCents()` over integer cents. Delete the unused currency field and conversion table. When multi-currency becomes a real requirement, add it then, with tests, knowing which currencies and rounding rules it needs.

**When not to apply** — Decisions that are costly to reverse deserve thought now: public API and wire formats, database keys, security, and data you cannot collect later (audit logs, timestamps). Building those to the current need while keeping the future change possible is not speculation.

**Related** — **Strategy** (`gof-patterns-typescript/patterns/strategy.md`) once a second real variant exists; [`speculative-generality`](speculative-generality.md); [`smallest-thing-that-works`](smallest-thing-that-works.md); [`rule-of-three`](../../dry-patterns/patterns/rule-of-three.md); **OCP** (`solid-patterns-typescript/patterns/ocp.md`) for extension points nobody extends.
