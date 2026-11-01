# Rule of Three

Leave the second copy alone; extract the shared part when the third copy appears.

Refs: https://en.wikipedia.org/wiki/Rule_of_three_(computer_programming)
Example: [examples/rule-of-three.py](../examples/rule-of-three.py)

**Principle** — Credited to Don Roberts and popularized by Martin Fowler in Refactoring (1999): "three strikes and you refactor". Two similar fragments do not yet show which parts vary. By the third, the cost of keeping copies in step outweighs the risk of choosing the wrong abstraction.

**Violation signals** — Overuse in one direction: a helper extracted after the first repeat, with a parameter added for the second caller. Neglect in the other: three or more pasted blocks with small edits, or a bug fixed in one copy and not the others. refactoring.guru lists the usual shapes under Duplicate Code.

**Fix** — With three real callers, extract only what all three share. In the example, `invoice_header`, `shipping_label` and `packing_slip` share a postal block, so `postal_block()` is extracted and the order line stays in `packing_slip`. Use Extract Function for code in one module and Pull Up Method or Template Method for sibling classes.

**When not to apply** — Three is a heuristic, not a count to hit. A security rule or tax formula should have one owner from the first copy. Three lines that match by coincidence stay apart (see knowledge-not-text).

**Related** — **Template Method** (`gof-patterns-typescript/patterns/template-method.md`) for sibling classes with the same steps; **Strategy** (`gof-patterns-typescript/patterns/strategy.md`) when copies differ in one algorithm; [`wrong-abstraction`](wrong-abstraction.md); [`knowledge-not-text`](knowledge-not-text.md); [`yagni`](../../kiss-patterns/patterns/yagni.md).
