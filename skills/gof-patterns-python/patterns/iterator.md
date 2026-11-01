# Iterator

Python's iteration protocol, usually implemented with a generator, gives sequential access without exposing structure.

Refs: https://refactoring.guru/design-patterns/iterator/python/example
Example: [examples/iterator.py](../examples/iterator.py)

**Intent** — Traverse a collection without revealing its internal representation.

**Problem** — A catalog stored as pages should be consumed as one stream of items.

**Applicability** — **Use** when a collection has a non-trivial traversal or should be consumed lazily. **Avoid** hand-written iterator classes with `__next__`: a generator function with `yield` and `yield from` does it, and a plain list or `itertools` helper often suffices.

**Python implementation** — `Catalog.__iter__` is a generator that does `yield from page.items`, so `for x in catalog` and `list(catalog)` work. Extra traversals are separate generator methods (`reversed_items`). Each call to `__iter__` creates a fresh generator, which lets multiple independent traversals coexist. Gotcha: a generator is single-use; if `__iter__` returned `self` you would lose that independence. Return type is `Iterator[str]` (or `Iterable`).

**Consequences** — Lazy, memory-friendly and works with the whole language. Cost: no random access or length unless you add them.

**Related patterns** — **Composite** trees are traversed with iterators; **Memento** can capture an iterator's position; **Visitor** walks structures with logic per type.
