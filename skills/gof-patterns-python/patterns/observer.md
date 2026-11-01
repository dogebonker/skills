# Observer

A subject keeps a list of subscribers and calls them when something happens.

Refs: https://refactoring.guru/design-patterns/observer/python/example
Example: [examples/observer.py](../examples/observer.py)

**Intent** — Notify many dependents about changes without the subject knowing who they are.

**Problem** — A price feed must update logging, alerts and charts, and the set changes at runtime.

**Applicability** — **Use** when one object's changes must trigger actions elsewhere and subscribers vary. **Avoid** the interface-and-class form when callbacks suffice: store plain `Callable`s. For async streams, prefer `asyncio.Queue` or an async generator; for in-process signals, a small event emitter library is common but unnecessary here.

**Python implementation** — `Listener = Callable[[str, float], None]`. `PriceFeed.subscribe` stores the callable and returns an unsubscribe closure; `publish` iterates over `list(self._listeners)`, a copy, so listeners can unsubscribe during dispatch. Bound methods (`Alerter(100).on_price`) and lambdas both work. Gotchas: the subject's list keeps subscribers alive, so use `weakref.WeakMethod` if lifetimes matter; one failing listener stops the rest unless you catch exceptions.

**Consequences** — Loose coupling and dynamic wiring. Cost: unpredictable order, memory leaks from forgotten subscriptions.

**Related patterns** — **Mediator** centralises the flow instead of broadcasting; **Command** can be what is notified; **Chain of Responsibility** stops at the first handler.
