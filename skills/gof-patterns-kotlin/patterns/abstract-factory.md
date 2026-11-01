# Abstract Factory

An interface with one creation function per product lets you build a whole matching family, such as tax rules and invoice format for one region.

Refs: https://refactoring.guru/design-patterns/abstract-factory/java/example
Example: [examples/abstract-factory.kt](../examples/abstract-factory.kt)

**Intent** — Create families of related objects without naming their concrete classes.

**Problem** — An app supports several regions. Each region needs a tax calculator and a formatter that belong together, and mixing EU tax with US formatting would be a bug.

**Applicability** — **Use** when products must be used together and the family is chosen once, for example by region, theme or backend. **Avoid** a factory interface with concrete factories when there is one product or the family is a few functions: Factory Method, or a data class of lambdas, is enough.

**Kotlin implementation** — Define `RegionFactory` with `createTax()` and `createFormatter()`, and implement it as `EuFactory` and `UsFactory`. `invoiceLine` takes only the interface, so swapping region is one argument. When a family has no state, a data class holding function types (`data class Region(val tax: (Double) -> Double, val format: ...)`) is shorter. Gotcha: a new product type forces a change in every factory, so keep families small and stable.

**Consequences** — You get consistency between products and an easy family swap. Adding a new product kind touches every factory.

**Related patterns** — **Factory Method** supplies each product method; **Singleton** often holds the factory; **Builder** assembles one complex object step by step.
