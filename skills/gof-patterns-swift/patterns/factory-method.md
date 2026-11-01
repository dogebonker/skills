# Factory Method

A protocol requirement that creates a product, so each conforming type chooses the concrete type it returns.

Refs: https://refactoring.guru/design-patterns/factory-method/swift/example
Example: [examples/factory-method.swift](../examples/factory-method.swift)

**Intent** — Let a base abstraction declare how a product is made while conformers decide which concrete product. Callers work only with the product protocol.

**Problem** — A workflow (exporting, parsing, rendering) needs an object but must not hard-code its concrete type, because new variants keep arriving.

**Applicability** — **Use** when a shared routine depends on a product whose concrete type varies by conformer, or a framework must let users plug in their own product. **Avoid** a protocol with a factory requirement when a plain function or an enum-switched `init` picks the type: a closure `() -> Product`, a metatype with an `init` requirement (`T.Type`), or a static `make(kind:)` is enough.

**Swift implementation** — Declare `protocol Exporter { func makeDocument(title:) -> any Document }` and put the shared `export(title:)` in a protocol extension, as `Exporter` does in the example. Return `any Document` from the factory method, or use an `associatedtype` when callers need the exact type. Prefer structs for creators. Do not subclass a creator class unless a framework forces it.

**Consequences** — Callers stay decoupled from concrete products and gain open extension. The cost is one extra conforming type per product kind.

**Related patterns** — **Abstract Factory** for families of products built by several factory methods; **Template Method** describes the shared `export`, which calls the factory method as one step; **Prototype** replaces subclassing with copying.
