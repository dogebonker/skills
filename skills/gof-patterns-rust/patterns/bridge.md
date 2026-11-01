# Bridge

A struct generic over an implementor trait: `Report<S: Sink>`.

Refs: https://refactoring.guru/design-patterns/bridge/rust/example
Example: [examples/bridge.rs](../examples/bridge.rs)

**Intent** — Separate what a thing does from how it does it, and let both sides grow independently.

**Problem** — Report kinds (summary, detailed) times output targets (console, memory, file) would otherwise need one type per combination.

**Applicability** — **Use** when two independent dimensions of variation would multiply into many types. **Avoid** two parallel traits when only one dimension varies: a trait with several implementations, or a generic function, is enough.

**Rust implementation** — Define the implementor trait `Sink`, then `struct Report<S: Sink> { sink: S }` holds one. Report methods call `self.sink.write(..)`. Adding a sink or a report method never touches the other side. Generics give static dispatch and let tests inject `MemorySink`. Use `Box<dyn Sink>` when the sink is chosen at runtime. The gotcha: generic parameters spread into every function that takes the abstraction, so accept `&mut impl` or a trait object at API edges to contain it.

**Consequences** — Two hierarchies grow without a combinatorial explosion. The cost is an extra layer, and in Rust a generic parameter that propagates.

**Related patterns** — **Adapter** fits an existing type, where Bridge is designed up front; **Strategy** for a Bridge with one varying behaviour; **Abstract Factory** for building the implementor side.
