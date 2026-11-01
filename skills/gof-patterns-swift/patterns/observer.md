# Observer

A publisher that pushes events to subscribers, in modern Swift an `AsyncStream`, Combine publisher, or `@Observable` model.

Refs: https://refactoring.guru/design-patterns/observer/swift/example
Example: [examples/observer.swift](../examples/observer.swift)

**Intent** — Define a one-to-many dependency so that when one object changes, its subscribers are notified.

**Problem** — A price feed must update a chart and an alert watcher that should not know about each other.

**Applicability** — **Use** when several consumers react to changes in one source and the set of consumers changes at runtime. **Avoid** a subscriber registry when a single consumer needs updates or SwiftUI state already handles view updates: a callback closure, or `@Observable`, `@State` or `@Published`, is enough.

**Swift implementation** — `PriceFeed` is an `actor` that hands out one `AsyncStream.makeStream(bufferingPolicy: .bufferingNewest(16))` per subscriber, keyed by id, and `publish` yields to every continuation, as the example does. A bounded buffer keeps a slow subscriber from growing memory without limit. `onTermination` removes a cancelled subscriber, so `publish` never yields into a dead stream. Consumers use `for await`. Call `finish()` to end the streams and clear the subscribers. For UI, use Observation (`@Observable`) or Combine's `PassthroughSubject`; `NotificationCenter` is the legacy global form. With closures, avoid retain cycles by capturing weakly.

**Consequences** — Loose coupling and live updates. Ordering, back pressure, and leaked subscriptions need attention.

**Related patterns** — **Mediator** centralizes the communication; **Command** can be the event; **Chain of Responsibility** passes to one receiver rather than all.
