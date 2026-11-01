# Facade

A small type whose few methods drive several subsystems, hiding their wiring and ordering.

Refs: https://refactoring.guru/design-patterns/facade/swift/example
Example: [examples/facade.swift](../examples/facade.swift)

**Intent** — Provide a simple interface to a complex set of classes.

**Problem** — Placing an order means calling inventory, payments and shipping in the right order with error handling.

**Applicability** — **Use** when callers need a high-level operation, or you want to isolate subsystems behind a boundary. **Avoid** a facade type when a single subsystem call suffices or the facade would only forward or rename one method: calling the subsystem directly is enough.

**Swift implementation** — Create a struct (`OrderFacade`) that owns the subsystems privately and exposes `throws` methods, returning results (the shipment and the charge) or domain errors via a nested `Error` enum, as in the example. `placeOrder` validates quantity and amount before touching any subsystem. The facade owns compensation: undo committed steps when a later step fails, as `placeOrder` releases the reservation when the charge is declined. Keep subsystem types accessible for advanced use. Inject subsystems through `init` for testing. In an app, a service or use-case type often plays this role.

**Consequences** — Less coupling and one place for orchestration. A facade can grow into a god object if everything is routed through it.

**Related patterns** — **Adapter** converts one interface; **Mediator** coordinates peers, Facade coordinates a subsystem one way; **Abstract Factory** can supply subsystems; **Singleton** is often misused for it.
