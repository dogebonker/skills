# Abstract Factory

A protocol with several `make...` methods that returns a consistent family of related products.

Refs: https://refactoring.guru/design-patterns/abstract-factory/swift/example
Example: [examples/abstract-factory.swift](../examples/abstract-factory.swift)

**Intent** — Produce families of related objects without naming their concrete types, and guarantee that products from one factory belong together.

**Problem** — Code needs a cache and a database that must match (local pair or production pair), and mixing them would be a bug.

**Applicability** — **Use** when the product family varies together (themes, platforms, environments) and clients must not mix variants. **Avoid** a factory protocol with concrete factories when there is one product or the family is chosen once at launch: Factory Method, a struct of closures, or plain injection of the products is enough.

**Swift implementation** — Define `StorageFactory` with `makeCache()` and `makeDatabase()`, then one struct per family (`LocalStorageFactory`, `ProductionStorageFactory`). Pass the factory into the client's `init`, as `OrderService` does. Use `any Cache` for the product types, or generics with associated types if you need static dispatch. A factory with no state should be a struct. Hold products in the client, not the factory, unless sharing is intended.

**Consequences** — Variants are swapped in one place and consistency is enforced by types. Adding a new product kind forces edits in every factory.

**Related patterns** — **Factory Method** for each individual product; **Singleton** for a global factory (prefer injection); **Facade** hides the subsystems it builds.
