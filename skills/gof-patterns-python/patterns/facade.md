# Facade

One class offers a simple method that coordinates several subsystem objects.

Refs: https://refactoring.guru/design-patterns/facade/python/example
Example: [examples/facade.py](../examples/facade.py)

**Intent** — Provide a simple entry point to a complex subsystem.

**Problem** — Placing an order means reserving stock, charging payment and scheduling shipping in the right order. Every caller repeating that is error-prone.

**Applicability** — **Use** when many callers need the same common sequence and should not know the subsystem's classes. **Avoid** a facade class when a single function does it: a module-level `place_order()` is a perfectly good facade, and Python modules themselves often act as facades via `__init__.py` re-exports.

**Python implementation** — `OrderFacade` builds `Inventory`, `Payments`, `Shipping` and exposes `place_order(...)`, returning a result string or an early "out of stock". It validates `qty > 0` first, and when `charge` fails it releases the reservation and re-raises. The facade owns compensation: undo committed steps when a later step fails. Accept the subsystem objects as constructor parameters if tests need substitutes. Keep the subsystem importable so advanced users can bypass the facade. Gotcha: do not let the facade grow business rules; it should only coordinate.

**Consequences** — Fewer dependencies for clients and one place to change the sequence. Cost: it can become a god object if it keeps absorbing logic.

**Related patterns** — **Adapter** wraps one object to convert its interface; **Mediator** coordinates peers that talk both ways; **Abstract Factory** can hide subsystem creation; **Singleton** (module global) holds one.
