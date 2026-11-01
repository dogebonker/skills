# Flyweight

A cache returning shared pointers to immutable values, with per-object state kept outside.

Refs: https://refactoring.guru/design-patterns/flyweight/go/example
Example: [examples/flyweight.go](../examples/flyweight.go)

**Intent** — Save memory by sharing the common part of many similar objects.

**Problem** — A map holds thousands of markers that all repeat the same icon bitmap.

**Applicability** — **Use** when a measured memory cost comes from many objects holding identical immutable data. **Avoid** a shared cache when the data is small or no memory problem has been measured: plain values, slices or `string` interning are enough.

**Go implementation** — Split intrinsic state (the shared `Icon`) from extrinsic state (position in `Marker`). A factory function (`IconFor`) looks up a map under a mutex and returns the same pointer for the same key. The shared value must be immutable, or goroutines will race on it. Go strings already share backing data on assignment, and `unique.Make` can intern comparable values. Gotcha: the cache grows without bound unless you evict.

**Consequences** — Large memory savings for repetitive data. The cost is a lookup, locking, and strict immutability of shared parts.

**Related patterns** — **Singleton** for exactly one instance, not many shared ones; **Composite** has leaves that are often flyweights; **Factory Method** resembles the cache lookup.
