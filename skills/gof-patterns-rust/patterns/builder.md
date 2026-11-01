# Builder

Methods that take `self` by value and return `Self`, optionally changing type as required fields are supplied (typestate).

Refs: https://refactoring.guru/design-patterns/builder/rust/example
Example: [examples/builder.rs](../examples/builder.rs)

**Intent** — Construct a complex value in steps and keep the half-built state out of the final type.

**Problem** — A request type has one required field and many optional ones. A constructor with eight arguments is unreadable, and `Option` fields leave invalid states representable.

**Applicability** — **Use** when construction has many optional parameters, or some fields are required and you want the compiler to enforce them. **Avoid** a builder type when a few fields and defaults suffice: a struct literal with `..Default::default()` is enough. Reach for a builder when defaults and validation need real logic.

**Rust implementation** — Chain methods that take `mut self` and return `Self`; this moves the builder along without borrowing. For required fields use typestate: `RequestBuilder<NoUrl>` only has `url()`, which returns `RequestBuilder<HasUrl>`, and only that type has `build()`. Calling `build()` too early is a compile error. The gotcha: with `&mut self` setters, `Builder::new().a().b()` returns `&mut Builder` that dies at the end of the statement, so consuming `self` is the safer default.

**Consequences** — Readable call sites and compile-time required fields. The cost is boilerplate.

**Related patterns** — **Factory Method** for simple creation without steps; **Prototype** for starting from a copy instead of from scratch; **State** for typestate, the same idea applied to builders.
