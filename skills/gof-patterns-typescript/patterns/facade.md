# Facade

A class with a few high-level methods that call several subsystem classes in the right order.

Refs: https://refactoring.guru/design-patterns/facade/typescript/example
Example: [examples/facade.ts](../examples/facade.ts)

**Intent** — Provide a simple interface to a complex subsystem.

**Problem** — Placing an order means reserving stock, charging, and scheduling shipping, and callers keep repeating and misordering those calls.

**Applicability** — **Use** when most callers need a small set of workflows and the subsystem details should stay out of their way. **Avoid** a facade class when a single exported function does it (`export function placeOrder(...)`): a module with a small public surface is already a facade. Use a class only when the facade holds state.

**TypeScript implementation** — `OrderFacade` owns the `Inventory`, `Billing` and `Shipping` collaborators as `private readonly` fields and exposes `placeOrder`. In a real codebase an ES module that exports only the high-level functions and keeps the rest unexported is the same pattern, enforced by the module boundary. `placeOrder` validates inputs first and releases the reservation when the charge fails. The facade owns compensation: undo committed steps when a later step fails. Gotcha: do not hide the subsystem so well that power users cannot reach it when they need to.

**Consequences** — Fewer dependencies for clients and one place to change workflow. A facade can grow into a god object if every feature is added to it.

**Related patterns** — **Adapter** converts one interface rather than simplifying many; **Mediator** coordinates peers rather than hiding them; **Singleton** is often applied to facades.
