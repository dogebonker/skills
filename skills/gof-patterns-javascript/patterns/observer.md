# Observer

Lets subjects notify any number of subscribers about changes without knowing who they are; in Node.js this is `EventEmitter`, in browsers `EventTarget`.

Refs: https://github.com/HowProgrammingWorks/Observer  
Example: [examples/observer.js](../examples/observer.js)

**Intent** — Define a one-to-many dependency so that when one object changes, its dependents are notified automatically.

**Problem** — Several parts of the system (email, audit, cache) must react to a change in an order, and the order object should not import them.

**Applicability** — **Use** for domain events, lifecycle hooks and UI updates. **Avoid** a hand-written `subscribe/notify` class when the platform has one: `EventEmitter` (or `EventTarget` for platform-agnostic code) is enough, and a plain callback is enough for exactly one listener.

**JS implementation** — `Order extends EventEmitter` and calls `emit('status', status, previous)` after changing its private state. Subscribers use `on`, `once` and `off` with a named function so it can be removed. Always remove listeners of long-lived emitters to avoid leaks. Listeners run synchronously in registration order. Gotcha: emitting `'error'` with no listener throws, and an exception in one listener stops the rest.

**Consequences** — Loose coupling and easy extension; control flow becomes implicit, and ordering and error handling are harder to follow.

**Related patterns** — **Mediator** for a central object that also decides routing; **Command** for events that are requests; **Chain of Responsibility** for handlers that may stop propagation.
