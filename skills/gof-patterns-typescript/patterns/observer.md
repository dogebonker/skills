# Observer

A subject keeps a set of listener functions and calls each when an event happens; `subscribe` returns an unsubscribe function.

Refs: https://refactoring.guru/design-patterns/observer/typescript/example
Example: [examples/observer.ts](../examples/observer.ts)

**Intent** — Notify many dependents automatically when one object changes.

**Problem** — A price changes and logging, alerts and a UI each need to react, without the source knowing about any of them.

**Applicability** — **Use** when one change must trigger others, and the set of listeners is dynamic. **Avoid** a hand-written Observer when `EventTarget`/`CustomEvent` or Node's `EventEmitter` fits; write one when you want typed payloads, as here.

**TypeScript implementation** — `Emitter<T>` stores `Set<Listener<T>>` in a `#private` field, and `emit` iterates over a copy so listeners can unsubscribe during dispatch. `subscribe` returns the remover, avoiding a separate `unsubscribe(fn)`. The payload type `T` is checked at both ends. Gotcha: forgotten unsubscribes leak memory, and one throwing listener stops the rest unless you catch.

**Consequences** — Loose coupling between source and reactions. Order of notification and cascading updates can be hard to reason about.

**Related patterns** — **Mediator** handles two-way coordination; **Command** can be the event payload; **Chain of Responsibility** lets only one receiver act.
