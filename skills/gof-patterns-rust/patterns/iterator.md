# Iterator

Implement the standard `Iterator` trait with `type Item` and `fn next`.

Refs: https://refactoring.guru/design-patterns/iterator/rust/example
Example: [examples/iterator.rs](../examples/iterator.rs)

**Intent** — Give clients sequential access to elements without revealing the underlying structure.

**Problem** — Paginated data must be consumed page by page, and callers should also be able to filter and count pages.

**Applicability** — **Use** when a collection or generator needs custom traversal order or lazy production. **Avoid** a custom `Iterator` when a slice, `Vec` or map already iterates the way you want: `.iter()`, `.windows()`, `.chunks()` or adaptors are enough.

**Rust implementation** — `impl Iterator for Pages<'_>` with `type Item = Page`. Implementing `next` unlocks every adaptor: `filter`, `map`, `take`, `count`. The iterator borrows the slice (`data: &'a [u32]`), so the collection cannot be mutated while it lives. Expose it through `IntoIterator` for `for` loops. The gotcha: an iterator that yields references into itself (a lending iterator) cannot be expressed with `Iterator`. Yield owned values or indexes, or borrow from the source with an explicit lifetime as done here.

**Consequences** — Lazy, composable traversal with zero cost. The cost is lifetime annotations when iterators borrow.

**Related patterns** — **Composite** is traversed by iterators; **Memento** for capturing iteration state; **Visitor** operates on elements, where an iterator visits them.
