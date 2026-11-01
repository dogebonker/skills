# Composite

Leaves and containers share one interface so client code treats a single item and a whole tree alike.

Refs: https://refactoring.guru/design-patterns/composite/python/example
Example: [examples/composite.py](../examples/composite.py)

**Intent** — Compose objects into tree structures and work with them uniformly.

**Problem** — Computing a folder's size should not require code that branches on file versus folder at every level.

**Applicability** — **Use** when data is naturally a part-whole tree (file systems, UI trees, expression nodes, org charts). **Avoid** a Composite class hierarchy when the structure is flat (use a `list`) or a nested `dict` and a recursive function is enough.

**Python implementation** — `Node` is a Protocol with `name` and `size()`. `File` returns its own bytes; `Folder` sums `c.size()` over `children`. Both are `@dataclass`es; `Folder.add` returns `self` to allow chaining. Use `field(default_factory=list)` for the children list, never a mutable default. Gotcha: recursion depth for very deep trees, and cycles if a node is added to its own descendant.

**Consequences** — Uniform treatment and easy new node kinds. Cost: the interface must suit both leaves and containers, so child management (`add`) lives only on containers here.

**Related patterns** — **Iterator** traverses a composite (use a generator); **Visitor** adds operations over the tree; **Decorator** shares the recursive composition shape; **Builder** constructs trees.
