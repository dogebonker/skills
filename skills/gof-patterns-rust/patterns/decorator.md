# Decorator

A generic wrapper struct that implements the same trait as the thing it wraps.

Refs: https://refactoring.guru/design-patterns/decorator/rust/example
Example: [examples/decorator.rs](../examples/decorator.rs)

**Intent** — Layer extra behaviour onto an object without changing it or subclassing.

**Problem** — A data source needs optional uppercase, reversal, compression or logging in any combination.

**Applicability** — **Use** when behaviours combine freely and must stack at runtime or compile time. **Avoid** a wrapper struct when a function transforms the value: a closure or iterator adaptor is enough.

**Rust implementation** — `struct Uppercase<D: DataSource>(D);` implements `DataSource` by calling the inner `read()` and transforming the result. Stacking `Reversed(Uppercase(FileSource(..)))` produces a concrete type with static dispatch and no allocation. When the stack is assembled at runtime use `Box<dyn DataSource>` as the inner type. Iterator adaptors (`map`, `filter`) in the standard library are decorators in exactly this style. The gotcha: long generic types make error messages hard to read, so name the final stack with a type alias or return `impl Trait`.

**Consequences** — Flexible composition without subclass explosion. The cost is many small types and nested generics.

**Related patterns** — **Proxy** has the same shape but controls access; **Adapter** changes the interface; **Chain of Responsibility** has handlers that may stop the flow.
