# Knowledge, Not Text

DRY asks that each fact about the system have one owner, not that similar-looking lines be merged.

Refs: https://www.artima.com/articles/orthogonality-and-the-dry-principle
Example: [examples/knowledge-not-text.py](../examples/knowledge-not-text.py)

**Principle** — Hunt and Thomas (The Pragmatic Programmer) define DRY over knowledge: every business rule, schema, format or decision gets one authoritative, unambiguous representation. Dave Thomas stresses in the Artima interview that this covers schemas, build files and docs, not only code. Two copies of one rule are duplication even when the text differs. Two different rules that look alike are not.

**Violation signals** — The same rate, limit or format written in different ways (`net * 1.2` and `net + net * 20 / 100`). A rule change that needs a search across files. Conversely, a shared constant like `LIMIT` used by two teams' rules that only match by coincidence.

**Fix** — Name the knowledge and give it one home: `VAT_RATE` and `gross()` replace both formulas. Keep coincidental matches apart: `MAX_CART_QUANTITY` and `MAX_RESTOCK_BATCH` are both 99 but change for different reasons.

**When not to apply** — Do not merge code just because it looks the same. Ask "if this rule changes, must the other copy change too?" If not, merging couples two owners and creates a wrong abstraction.

**Related** — **Template Method** (`gof-patterns-typescript/patterns/template-method.md`) when the shared knowledge is a fixed step sequence; [`single-source-of-truth`](single-source-of-truth.md) for where the owner lives; [`wrong-abstraction`](wrong-abstraction.md) for the cost of merging coincidences; **SRP** (`solid-patterns-typescript/patterns/srp.md`), since a reason to change marks a piece of knowledge.
