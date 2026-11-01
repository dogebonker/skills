# Adapter

A wrapper type, or an extension, that makes an existing API conform to the protocol your code expects.

Refs: https://refactoring.guru/design-patterns/adapter/swift/example
Example: [examples/adapter.swift](../examples/adapter.swift)

**Intent** — Convert the interface of one type into another interface that clients expect so incompatible types can collaborate.

**Problem** — A third-party or legacy API has the right behavior but the wrong shape (units, names, return types).

**Applicability** — **Use** when you must reuse a type you cannot change, or isolate a vendor SDK behind your own protocol. **Avoid** an adapter type when you own the type or the mismatch is a single value conversion: renaming or adding the method, or a closure, is enough.

**Swift implementation** — Define your protocol (`PaymentGateway`) and a struct wrapping the foreign type (`LegacyBillingAdapter`) that converts units and results. For a small mismatch, conform the foreign type through an `extension`, as the example shows with `LegacyBillingSDK`. Use `some PaymentGateway` in callers. Extensions cannot hold stored state, so use a wrapper if the adapter needs any.

**Consequences** — The client code stays clean and the vendor can be swapped. There is one more layer to maintain.

**Related patterns** — **Bridge** is designed up front, Adapter after the fact; **Decorator** keeps the interface while Adapter changes it; **Facade** simplifies, Adapter converts; **Proxy** keeps the same interface.
