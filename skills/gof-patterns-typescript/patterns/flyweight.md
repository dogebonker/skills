# Flyweight

Immutable shared objects, looked up in a `Map` cache, hold the repeated state while each instance keeps only its unique fields.

Refs: https://refactoring.guru/design-patterns/flyweight/typescript/example
Example: [examples/flyweight.ts](../examples/flyweight.ts)

**Intent** — Fit many objects in memory by sharing the parts of their state that repeat.

**Problem** — A document with a million characters would store font, size and weight in every glyph, though only a handful of combinations exist.

**Applicability** — **Use** when a program creates huge numbers of similar objects, much of their state is immutable and repeated, and memory is measurably a problem. **Avoid** a flyweight cache when primitives, interned strings, and small numbers are already shared. Measure first; for a few thousand objects the pattern adds complexity for no gain.

**TypeScript implementation** — `StyleCache.get` builds a key from the parameters and returns a frozen `GlyphStyle` from a `Map`, creating it once. `Glyph` stores `char`, `x` and a reference to the shared style. Mark shared state `readonly` and `Object.freeze` it so no holder can mutate it for everyone. For object keys use `WeakMap`. Gotcha: mutable flyweights cause action at a distance.

**Consequences** — Large memory savings for repetitive data. Code gets a factory and a split between shared and unique state.

**Related patterns** — **Singleton** shares one object, not many; **Composite** leaves are often flyweights; **Factory Method** is the shape of the cache lookup.
