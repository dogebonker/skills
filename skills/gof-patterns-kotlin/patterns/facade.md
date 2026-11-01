# Facade

A small class offers one simple function over several subsystem classes and keeps their wiring in one place.

Refs: https://refactoring.guru/design-patterns/facade/java/example
Example: [examples/facade.kt](../examples/facade.kt)

**Intent** — Provide a simple interface to a complex set of classes.

**Problem** — Checkout touches inventory, payments and shipping. Every screen repeating the three calls in the right order and with the right error handling is fragile.

**Applicability** — **Use** when callers need a few common operations and should not know the subsystem order or details. **Avoid** a facade class when one call into one class is already simple: calling it directly is enough, and a repository or use case class often already plays this role.

**Kotlin implementation** — `CheckoutFacade` takes the three subsystems with default arguments and exposes `buy(...)`. It checks `qty` and the price with `require` before touching any subsystem, returns null on failure, and returns an `Order` holding the tracking id and the charge on success. The facade owns compensation: undo committed steps when a later step fails, as `buy` releases the reservation when the charge is declined. Default parameters make it usable in production and replaceable in tests. In Android architecture a repository facades network, database and cache for the ViewModel, and a `UseCase` class often does the same for domain steps. Gotcha: keep the facade thin and do not let it grow business rules, or it becomes a god class. Subsystems stay accessible for callers that need more.

**Consequences** — Less coupling and one place to change when subsystems change. A facade can hide useful flexibility.

**Related patterns** — **Adapter** makes one class fit an interface; **Mediator** coordinates two-way communication; **Singleton** often provides the single facade instance.
