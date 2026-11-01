# Observer

A subject that fans events out to subscriber channels or callbacks, with `context.Context` ending a subscription.

Refs: https://refactoring.guru/design-patterns/observer/go/example
Example: [examples/observer.go](../examples/observer.go)

**Intent** — Define a one-to-many dependency so subscribers are notified when the subject changes.

**Problem** — A price feed must notify a UI and an alert service, and either may come and go.

**Applicability** — **Use** when one source has many independent consumers that can be added or removed at runtime. **Avoid** a subscriber registry when there is one consumer: call it directly or take a callback parameter.

**Go implementation** — `Subject.Subscribe(ctx)` returns a receive-only buffered channel, and cancelling `ctx` unsubscribes and closes it through `context.AfterFunc`, with no goroutine parked per subscriber. `Publish` uses a non-blocking `select` so one slow subscriber cannot stall the rest. Callbacks (`func(Event)`) are simpler when everything runs in one goroutine; channels fit when subscribers run concurrently. Gotchas: always close or unsubscribe to avoid goroutine leaks, never send on a closed channel, and decide whether to drop or block when a buffer fills.

**Consequences** — Loose coupling and dynamic subscribers. The cost is hidden control flow, goroutine lifecycle to manage, and a delivery policy to define.

**Related patterns** — **Mediator** lets participants also talk back through a hub; **Command** packages the event as an action; **Chain of Responsibility** lets one handler consume the event.
