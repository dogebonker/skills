# Iterator

Conform to `Sequence` and `IteratorProtocol` so a collection is traversable with `for-in` and the standard algorithms.

Refs: https://refactoring.guru/design-patterns/iterator/swift/example
Example: [examples/iterator.swift](../examples/iterator.swift)

**Intent** — Traverse the elements of a collection without exposing its representation.

**Problem** — A custom container needs a defined traversal order, or you need a lazy or infinite series.

**Applicability** — **Use** when callers must walk a custom structure, or several different traversals of the same data are needed. **Avoid** a custom `IteratorProtocol` type when the data is an array or dictionary you can return, or the series is generated: the collection itself, `sequence(first:next:)`, or `AsyncStream` for asynchronous values is enough.

**Swift implementation** — Implement `makeIterator()` returning a struct that conforms to `IteratorProtocol` with a `mutating func next() -> Element?`, as `Playlist.ReverseIterator` does. You then get `map`, `filter` and `for-in` free. Conform to `Collection` instead if you need indexing and multiple passes. Iterators are value types, so copies traverse independently, which is a gotcha for class-backed iterators.

**Consequences** — Uniform traversal and lazy evaluation. A single-pass `Sequence` can be consumed once, which surprises callers.

**Related patterns** — **Composite** is what you often iterate; **Visitor** applies an operation per element; **Memento** can save an iterator's position.
