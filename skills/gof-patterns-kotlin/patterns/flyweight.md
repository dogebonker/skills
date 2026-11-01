# Flyweight

Share immutable objects that hold intrinsic state through a cache, and keep only per-use state in each client object.

Refs: https://refactoring.guru/design-patterns/flyweight/java/example
Example: [examples/flyweight.kt](../examples/flyweight.kt)

**Intent** — Reduce memory by sharing the common part of many similar objects.

**Problem** — A map shows thousands of markers. Each one carrying its own copy of an icon bitmap wastes memory.

**Applicability** — **Use** when there are very many objects, much of their state is identical and immutable, and memory is measurably a problem. **Avoid** a flyweight cache when the shared values are small or already interned: enums, `String` literals and boxed small integers are enough, since they are flyweights already. Android also caches bitmaps through `LruCache` and image libraries.

**Kotlin implementation** — `MapIcon` is the immutable shared part and `Marker` holds only `x`, `y` and a reference to its icon. `IconFactory.get(name)` uses `getOrPut` so each name loads once. The `===` check in `main` shows identity. Make the shared class immutable, because mutation by one marker would affect every marker. A plain `HashMap` is not thread safe, so use `ConcurrentHashMap` or confine access to one thread when the factory is shared. Prefer measuring first. For bitmap-like data, `LruCache` bounds memory, where a permanent map keeps everything forever.

**Consequences** — Large memory savings when sharing is real. Code is more complex, and extrinsic state must be passed around.

**Related patterns** — **Singleton** for one instance, not one per key; **Composite** for shared leaves in a tree; **Factory Method** often hides the cache behind a factory.
