# Bridge

Two protocol hierarchies connected by composition, so abstraction and implementation vary independently.

Refs: https://refactoring.guru/design-patterns/bridge/swift/example
Example: [examples/bridge.swift](../examples/bridge.swift)

**Intent** — Split a concept into an abstraction and an implementation, and let each evolve on its own.

**Problem** — Notification kinds (alert, receipt) times channels (email, SMS) would otherwise need a type per combination.

**Applicability** — **Use** when two dimensions of variation exist, and combinations would explode with plain subtyping. **Avoid** an abstraction and implementation split when only one dimension varies: a single protocol, or a closure passed in, is enough.

**Swift implementation** — Model the implementation as a protocol (`Channel`) and the abstraction as another protocol (`Notification`) whose requirement is a `channel` property. Put the shared `send()` in a protocol extension, as the example does. Concrete notifications are structs holding any `Channel`. Use `any Channel` for runtime choice or a generic parameter for static dispatch.

**Consequences** — N plus M types instead of N times M, with swappable parts at runtime. It needs foresight and adds indirection.

**Related patterns** — **Strategy** is the same structure with one varying algorithm; **Adapter** fixes mismatches afterward; **Abstract Factory** can build the implementation side.
