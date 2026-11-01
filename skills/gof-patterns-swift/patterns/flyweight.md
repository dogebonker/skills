# Flyweight

Share immutable intrinsic state between many small objects, using a cache keyed by that state.

Refs: https://refactoring.guru/design-patterns/flyweight/swift/example
Example: [examples/flyweight.swift](../examples/flyweight.swift)

**Intent** — Save memory by sharing the common part of objects instead of storing it in each one.

**Problem** — Rendering thousands of glyphs or tiles where each repeats the same font, texture or style data.

**Applicability** — **Use** when you have a very large number of objects, most of their state is identical and immutable, and profiling shows memory pressure. **Avoid** a flyweight cache when values are small or memory pressure is not measured: plain structs are enough, since they are compact and copy-on-write collections share storage.

**Swift implementation** — Make the shared part an immutable `final class` marked `Sendable` (`GlyphStyle`), cache instances in a `StyleCache` keyed by a `Hashable` struct of their parameters (`Key`), which avoids string-key collisions, and keep the extrinsic state (character, position) in a lightweight struct (`Glyph`) that references the shared object, as the example does. Compare with `===` to prove sharing. Guard the cache with an actor or lock if used across threads.

**Consequences** — Large memory savings for repeated data. Lookup cost and complexity grow, and shared state must stay immutable.

**Related patterns** — **Singleton** for the cache, though not required; **Composite** often has flyweight leaves; **Factory Method** produces the shared objects; **Prototype** is an alternative for creation.
