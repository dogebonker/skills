# Factory Method

A function (or associated function) that returns a trait object or an enum-selected value, so callers never name the concrete type.

Refs: https://refactoring.guru/design-patterns/factory-method/rust/example
Example: [examples/factory-method.rs](../examples/factory-method.rs)

**Intent** — Move the choice of concrete type into one place and hand callers a value they use through a common trait.

**Problem** — Code that calls `Email::new` or `Sms::new` directly is welded to those types, and adding a channel means editing every call site.

**Applicability** — **Use** when the concrete type depends on runtime input such as config, a request field or a feature flag, and callers only need the shared behaviour. **Avoid** a factory function when every call site knows the type at compile time: `Type::new()` or a generic parameter `T: Notifier` is enough.

**Rust implementation** — Define the product as a trait (`Notifier`) and the factory as a free function `create_notifier(Channel) -> Box<dyn Notifier>` that `match`es on an enum. `Box<dyn Trait>` is required only because the size and type are chosen at runtime. A closed set of products can be an enum instead, with no box. The gotcha: a trait with generic methods, methods returning `Self`, or a `Sized` supertrait is not dyn compatible (formerly "object safe"); add `where Self: Sized` to those methods to keep it boxable.

**Consequences** — Callers stay independent of concrete types. The cost is a heap allocation per product and a central `match` that grows.

**Related patterns** — **Abstract Factory** for a family of related products created together; **Builder** for a product with many optional parts; **Strategy** for swapping behaviour rather than creating objects.
