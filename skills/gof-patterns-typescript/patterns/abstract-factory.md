# Abstract Factory

An interface of `create…()` methods, implemented once per product family, so client code gets matching objects without naming concrete types.

Refs: https://refactoring.guru/design-patterns/abstract-factory/typescript/example
Example: [examples/abstract-factory.ts](../examples/abstract-factory.ts)

**Intent** — Create families of related objects that must be used together, without coupling the client to their classes.

**Problem** — Mixing a cloud A blob store with a cloud B queue breaks assumptions, and the client should not decide each product separately.

**Applicability** — **Use** when the system must work with several product families and enforce that products from one family are never mixed. **Avoid** an Abstract Factory hierarchy when there is only one family or one product: a Factory Method or a plain function is enough. A single object literal of functions often replaces the whole hierarchy.

**TypeScript implementation** — Model the factory as an `interface CloudFactory` and implement it with object literals (`awsFactory`, `localFactory`), not classes. Check the literals with `satisfies Record<string, CloudFactory>` so keys stay inferred while shapes are validated. Pass the factory into `archiveReport` rather than importing a global. Gotcha: adding a product to the interface forces every family to change.

**Consequences** — Families stay consistent and swapping a family is one argument. The interface grows with every new product kind, and every family must follow.

**Related patterns** — **Factory Method** creates a single product that varies; **Singleton** often holds one factory instance per family.
