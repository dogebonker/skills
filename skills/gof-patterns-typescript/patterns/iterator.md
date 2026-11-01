# Iterator

A class implements `[Symbol.iterator]`, usually as a generator, so `for...of`, spread and destructuring work on it.

Refs: https://refactoring.guru/design-patterns/iterator/typescript/example
Example: [examples/iterator.ts](../examples/iterator.ts)

**Intent** — Traverse a collection without exposing its internal structure.

**Problem** — Orders come back in pages with links to the next page, and callers want a simple loop over all of them.

**Applicability** — **Use** when you need a custom traversal order, lazy or paginated sequences, or a uniform way to walk different structures. **Avoid** an iterator class when arrays, `Map` and `Set` already iterate. Use `array.entries()` or a generator function before writing an iterator class.

**TypeScript implementation** — `PagedOrders implements Iterable<string>` and defines `*[Symbol.iterator]()`, using `yield*` to delegate to each page's items. The generator keeps position in local variables, so no iterator class is needed. For async sources use `Symbol.asyncIterator` with `for await`. Gotcha: a generator-backed iterable can often be consumed only once if the state lives outside the method.

**Consequences** — Lazy, uniform traversal that hides storage. Little cost, since the language supports it directly.

**Related patterns** — **Composite** for the trees you traverse; **Visitor** operates on elements while you traverse; **Memento** snapshots the position.
