# Strategy

A generic parameter `F: Fn(..) -> ..`, so any function or closure is a strategy.

Refs: https://refactoring.guru/design-patterns/strategy/rust/example
Example: [examples/strategy.rs](../examples/strategy.rs)

**Intent** — Make algorithms interchangeable behind a common signature.

**Problem** — Shipping cost is flat, by weight, or free over a threshold, and the cart must not care which.

**Applicability** — **Use** when several ways to do one job exist and the choice is made by the caller or config. **Avoid** a strategy trait when a closure or `fn` item suffices, which is nearly always: define a trait only when a strategy needs several methods or its own state.

**Rust implementation** — `fn total<F: Fn(u32) -> u64>(&self, shipping: F) -> u64`. Pass `shipping_flat`, `shipping_by_weight` or a closure capturing local values. Generics monomorphise, so there is no indirection. Store a strategy in a struct as a type parameter, or as `Box<dyn Fn(u32) -> u64>` when it is chosen at runtime. Choose `Fn` if it is called repeatedly without mutation, `FnMut` if it keeps state, `FnOnce` if consumed. The gotcha: a struct field of closure type needs a generic parameter or a box, since every closure has a unique type.

**Consequences** — Minimal code and zero cost. The cost is that a stored closure type leaks into struct generics.

**Related patterns** — **State** has the same shape but is self-driven; **Template Method** varies steps inside a fixed skeleton; **Command** for a deferred or undoable action.
