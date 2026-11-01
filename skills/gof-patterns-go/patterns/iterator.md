# Iterator

A function of type `iter.Seq` or `iter.Seq2` consumed with `for range` (Go 1.23+).

Refs: https://refactoring.guru/design-patterns/iterator/go/example
Example: [examples/iterator.go](../examples/iterator.go)

**Intent** — Provide a way to access the elements of a collection sequentially without exposing its representation.

**Problem** — A playlist stores tracks in a slice today and may use a tree tomorrow, but callers just want to loop.

**Applicability** — **Use** when a type has non-trivial traversal (trees, paginated APIs, generators) or several traversal orders. **Avoid** a custom iterator when the data is a slice or map: `range` over it directly.

**Go implementation** — Return `iter.Seq[T]` or `iter.Seq2[K, V]` from methods such as `All()` and `Reverse()`. The function calls `yield(v)` for each element and must stop when `yield` returns false, which makes `break` work. Callers use `for i, t := range p.All()`. Use `iter.Pull` only when you need pull-style `next()` control. Standard helpers `slices.Collect` and `maps.Keys` build on this. Gotcha: ignoring `yield`'s return value panics when the loop exits early.

**Consequences** — Native loops over any structure, lazy and allocation-light. The cost is the yield-callback style, which is harder to read than a plain slice.

**Related patterns** — **Composite** is a common traversal target; **Visitor** runs operations over elements instead of exposing them; **Memento** can capture the iteration position.
