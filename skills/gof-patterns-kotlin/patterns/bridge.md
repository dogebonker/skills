# Bridge

Hold an interface reference in an abstraction class so that two hierarchies, what is reported and how it is written, vary independently.

Refs: https://refactoring.guru/design-patterns/bridge/java/example
Example: [examples/bridge.kt](../examples/bridge.kt)

**Intent** — Split a large class into an abstraction and an implementation that can change separately.

**Problem** — Report types (sales, errors) and output formats (plain, markdown) multiply into one class per pair if you subclass for both.

**Applicability** — **Use** when two independent dimensions of variation would otherwise create a class explosion. **Avoid** a second interface hierarchy when one dimension varies or the implementation is a single behaviour: a function-type parameter is enough.

**Kotlin implementation** — `Report` takes an `Output` in its constructor and `SalesReport` and `ErrorReport` call `output.write(...)`. Adding `HtmlOutput` needs no new report class, and adding a report needs no new output class. Use composition through a constructor parameter, which Kotlin makes cheap with `protected val`. If `Output` has one method, make it a `fun interface` or a lambda. On Android, `View` and its rendering `Canvas`, or a repository over swappable data sources, show the same split. Gotcha: design the implementation interface around primitive operations, not around one abstraction's needs.

**Consequences** — Dimensions grow additively. You pay an extra interface and an indirection up front.

**Related patterns** — **Strategy** has the same shape but swaps one behaviour; **Adapter** fits existing classes after the fact; **Abstract Factory** can build the implementation side.
