# Mediator

A central object, an `actor` when state is shared, that coordinates peers so they never reference each other.

Refs: https://refactoring.guru/design-patterns/mediator/swift/example
Example: [examples/mediator.swift](../examples/mediator.swift)

**Intent** — Reduce chaotic dependencies between objects by making them talk only through a mediator.

**Problem** — Chat participants, form fields, or UI components would otherwise hold references to each other.

**Applicability** — **Use** when many-to-many interactions are tangled and components should be reusable without knowing their peers. **Avoid** a mediator object when two objects interact directly or an `@Observable` model drives the views: a delegate, a closure, or the shared model is enough.

**Swift implementation** — Make the mediator an `actor` (`ChatRoom`) owning the peer state, so concurrent senders cannot race, and let participants hold only the room, as the example does. `join` creates an inbox only when absent, so rejoining keeps messages. Participant values are `Sendable` structs and calls are `await`ed. In UIKit, a view controller often acts as mediator; in SwiftUI, a shared observable model does. Avoid letting the mediator grow into a god object.

**Consequences** — Peers become reusable and rules live in one place. The mediator can become complex and a single point of failure.

**Related patterns** — **Observer** is a decentralized way to notify; **Facade** is a one-way simplification; **Command** can carry messages through it.
