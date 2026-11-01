# Iterator

Implement `Iterable` or return a `Sequence` built with `sequence { yield(...) }`, and let the compiler keep the traversal state.

Refs: https://refactoring.guru/design-patterns/iterator/java/example
Example: [examples/iterator.kt](../examples/iterator.kt)

**Intent** — Traverse a collection without exposing how it is stored.

**Problem** — A page tree can be walked depth first or breadth first, and callers should use `map`, `filter` and `for` without knowing the structure.

**Applicability** — **Use** when a custom data structure needs traversal, or several traversal orders are needed over the same data. **Avoid** a custom `Iterator` class when the data is already a `List`, `Set` or `Map`, or a simple generated series: `for` with collection functions, or `generateSequence`, is enough.

**Kotlin implementation** — `Page : Iterable<Page>` returns `sequence { yield(this@Page); for (child in children) yieldAll(child) }.iterator()`. That is depth first, written in three lines. `Page.breadthFirst()` is an extension returning a `Sequence`, so each order is a named function. Sequences are lazy: `firstOrNull` stops early. `iterator { }` builds an `Iterator` directly. Gotcha: a `Sequence` may be consumed only once for some sources, and a mutable collection changed while iterating throws `ConcurrentModificationException`. Android's `Cursor` is a hand-written iterator.

**Consequences** — Clean traversal with little code and lazy evaluation. Recursion inside `sequence` allocates per level.

**Related patterns** — **Composite** for the structure being walked; **Visitor** performs operations during a traversal; **Memento** can save an iteration position.
