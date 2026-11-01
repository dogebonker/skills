# Decorator

A wrapper that conforms to the same protocol as what it wraps and adds behavior before or after delegating.

Refs: https://refactoring.guru/design-patterns/decorator/swift/example
Example: [examples/decorator.swift](../examples/decorator.swift)

**Intent** — Attach responsibilities to an object dynamically by wrapping it, keeping the same interface.

**Problem** — Logging, caching, uppercase conversion and similar add-ons must combine freely without a subtype per combination.

**Applicability** — **Use** when behaviors are optional, stackable, and chosen at runtime or composition time. **Avoid** a wrapper type when the added behavior is a single transformation: a function (`map`, closure composition), a property wrapper, or a SwiftUI view modifier is enough.

**Swift implementation** — Write generic wrappers `UppercasedSource<Base: DataSource>` and chain them with protocol-extension helpers (`.uppercased().logged()`), as the example does. Generics keep the stack statically typed and fast; use `any DataSource` if the stack is chosen dynamically. For property-level decoration use `@propertyWrapper`; for UI use `ViewModifier`.

**Consequences** — Flexible composition without class explosion. Long stacks are hard to debug and ordering matters.

**Related patterns** — **Proxy** shares the shape but controls access; **Adapter** changes the interface; **Chain of Responsibility** also chains but may stop; **Composite** wraps many children.
