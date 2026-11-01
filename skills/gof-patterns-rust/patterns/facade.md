# Facade

A struct owning the subsystem values and exposing a few high-level methods.

Refs: https://refactoring.guru/design-patterns/facade/rust/example
Example: [examples/facade.rs](../examples/facade.rs)

**Intent** — Offer a small interface over a group of collaborating components.

**Problem** — Placing an order means reserving stock, charging a card and scheduling shipping, and callers keep getting the order wrong.

**Applicability** — **Use** when clients should use a simple entry point and not know about subsystem internals. **Avoid** a facade struct when the subsystem is one call: a free function is enough, since wrapping a single type adds nothing.

**Rust implementation** — `OrderFacade` holds `Inventory`, `Payments`, `Shipping` and exposes `place_order`. Inside, the `?` operator hides error plumbing between steps. Keep the subsystem types public if power users need them, as Rust modules let you re-export only the facade by default. A module with a few `pub fn` is often the entire facade. The gotcha: the facade owns compensation, so make partial failure explicit in the return type and undo committed steps when a later step fails (the example releases the reservation when the charge fails).

**Consequences** — Less coupling and one place to change workflow. The cost is that the facade can grow into a god object.

**Related patterns** — **Adapter** wraps one type to change its interface; **Mediator** coordinates peers that talk both ways; **Singleton** is often how a facade is shared.
