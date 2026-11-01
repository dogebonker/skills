# Chain of Responsibility

An ordered `Vec` of handlers, each returning `Option<Response>`; `find_map` runs the chain.

Refs: https://refactoring.guru/design-patterns/chain-of-responsibility/rust/example
Example: [examples/chain-of-responsibility.rs](../examples/chain-of-responsibility.rs)

**Intent** — Let several handlers get a chance at a request, in order, without the sender knowing which one acts.

**Problem** — A request must pass authentication, rate limiting and routing, each of which may reject it.

**Applicability** — **Use** when processing steps are ordered, optional and independently configurable. **Avoid** a linked handler chain when the sequence is fixed: function calls joined with `?` are enough. Link handlers only when they are assembled at runtime.

**Rust implementation** — `trait Handler { fn handle(&self, req: &Request) -> Option<String>; }`, then `Chain(Vec<Box<dyn Handler>>)` with `self.0.iter().find_map(|h| h.handle(req))`. Returning `Some` stops the chain, and `None` passes control on. This avoids the linked-list `Option<Box<dyn Handler>>` plus `next` pointer of the textbook version and its ownership puzzles. For middleware that wraps the rest of the chain (like tower layers), pass a `next: &dyn Fn(&Request) -> Response` instead. The gotcha: ordering matters, so test it.

**Consequences** — Decoupled, reorderable handlers. The cost is that a request can fall off the end unhandled, so decide on a default.

**Related patterns** — **Command** for requests as objects to pass along; **Decorator** wraps without stopping; **Composite** for chains that often form trees.
