# Facade

A struct whose few methods orchestrate the subsystem types behind them.

Refs: https://refactoring.guru/design-patterns/facade/go/example
Example: [examples/facade.go](../examples/facade.go)

**Intent** — Offer a simplified interface to a complex set of types.

**Problem** — Placing an order means reserving stock, charging a card and booking a shipment in the right order, and every caller repeats that sequence.

**Applicability** — **Use** when a subsystem has many moving parts and most callers need only a handful of high-level operations. **Avoid** a facade when the subsystem is already small or callers legitimately need its details: call the parts directly.

**Go implementation** — Make a struct (`OrderService`) holding the subsystem values and expose methods like `Place` that run the steps and wrap errors with `%w`, as the example shows. The facade owns compensation: undo committed steps when a later step fails (the example releases the reservation when the charge fails), and validate inputs before the first step. Keep subsystem types usable on their own so power users can bypass the facade. In Go, a package whose exported API is a few functions is itself a facade; unexported types hide the rest. Gotcha: a facade that grows every feature becomes a god object.

**Consequences** — Less coupling and one place for the workflow. The cost is another layer that can drift from the subsystems.

**Related patterns** — **Adapter** converts one interface rather than simplifying many; **Mediator** is a hub that components talk through both ways; **Singleton** is often how a facade is created once.
