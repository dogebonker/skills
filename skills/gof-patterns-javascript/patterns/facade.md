# Facade

Simplifies access to a complex system, providing a unified and clear interface, hiding and protecting internal complexity.

Refs: https://github.com/HowProgrammingWorks/Facade  
Example: [examples/facade.js](../examples/facade.js)

**Intent** — One narrow API orchestrates caches, IO, schedulers, or subsystems so feature code stays linear.

**Problem** — Integrations sprawl across many objects with easy-to-get-wrong ordering.

**Applicability** — **Use** at module boundaries and app services. **Avoid** one app-wide facade that grows into a god object: one facade per bounded context is enough.

**JS implementation** — Factory returning a plain object of async methods: `createApi` over db, cache and logger, `createCheckout` over inventory, payments and shipping. `placeOrder` validates quantity and amount before touching any subsystem and returns the charge result. The facade owns compensation: undo committed steps when a later step fails. Gotcha: a rejected `await` skips every later line, so the release goes in `catch` around the charge, not after it.

**Consequences** — Faster feature work; facades need versioning when internals change behavior.

**Related patterns** — **Adapter** for each foreign subsystem the facade sits over; **Mediator** coordinates peers in both directions, while a facade only calls down.
