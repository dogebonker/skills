# Strategy

A function value, typically a closure stored in a property, that supplies an interchangeable algorithm.

Refs: https://refactoring.guru/design-patterns/strategy/swift/example
Example: [examples/strategy.swift](../examples/strategy.swift)

**Intent** — Define a family of algorithms, make them interchangeable, and let the client choose one.

**Problem** — Shipping cost, sorting, or pricing rules vary and `if` branches keep growing.

**Applicability** — **Use** when several ways to do the same job exist and the caller or configuration picks one. **Avoid** a strategy protocol with one conforming type per algorithm when each algorithm is one function: a closure or function reference is enough.

**Swift implementation** — Declare `typealias ShippingCost = (Double) -> Double`, define strategies as closures, and store one in `Checkout`, as the example does. Swap it by assignment. The standard library's `sorted(by:)` is this pattern. Use a protocol with `some`/`any` only when a strategy needs several methods or state. Mark closures `@Sendable` when they cross threads, and `@escaping` on parameters you store.

**Consequences** — Algorithms are swappable and testable alone. Clients must know which to pick.

**Related patterns** — **State** is similar but self-switching; **Template Method** varies steps via inheritance, Strategy via composition; **Command** wraps an action with undo; **Decorator** changes behavior by wrapping.
