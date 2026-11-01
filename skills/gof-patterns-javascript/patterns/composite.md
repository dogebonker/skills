# Composite

Implements a common interface to uniformly handle individual objects and their tree structures, e.g., DOM or file systems.

Refs: https://github.com/HowProgrammingWorks/Composite  
Example: [examples/composite.js](../examples/composite.js)

**Intent** — Treat part and whole with the same operation (sum, render, serialize) via recursion or uniform traversal.

**Problem** — Nested aggregates (menus, folders, JSON) should not need `if (isLeaf)` at every level.

**Applicability** — **Use** for trees and DAGs with shared algorithms (totals, permissions walk). **Avoid** a composite when the structure is flat: `map` or `reduce` over the list is enough.

**JS implementation** — `Array.isArray` vs object values, `reduce` + recursion; JSON trees as in the example. A value that is neither a priced item nor an object throws a `TypeError` instead of turning the total into `NaN`. Gotcha: recursion does not stop on cycles, so a graph that is not a tree overflows the stack unless visited nodes are tracked in a `Set`.

**Consequences** — Simple client code; deep stacks on huge trees—consider iteration APIs if needed.

**Related patterns** — **Iterator** for flattening the tree into `for...of`; **Decorator** for attaching cross-cutting node metadata.
