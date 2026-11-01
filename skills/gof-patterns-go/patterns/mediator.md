# Mediator

A hub object that components call, which then forwards to the right participants.

Refs: https://refactoring.guru/design-patterns/mediator/go/example
Example: [examples/mediator.go](../examples/mediator.go)

**Intent** — Centralize communication between objects so they refer to the hub instead of each other.

**Problem** — Chat users that hold references to every other user make joins and leaves touch everyone.

**Applicability** — **Use** when components interact in complex but well-defined ways, and you want to reuse them without knowing their peers. **Avoid** a mediator when two objects talk or a simple channel fan-out expresses the flow: a direct call or the channel is enough.

**Go implementation** — Write a `ChatRoom` that holds participants in a map and exposes `Join` and `Broadcast`; participants keep a pointer to the room and call `Say`, as in the example. A small mediator interface defined by the participants lets you swap or fake the hub in tests. For concurrent use, guard the map with a mutex or run the hub in a goroutine that owns its state and receives messages on a channel. Gotcha: the mediator can become a god object holding all the logic.

**Consequences** — Peers become decoupled and interaction rules live in one place. The cost is a central type that can grow too large.

**Related patterns** — **Observer** is a hub that broadcasts events one way; **Facade** simplifies access but is not a two-way hub; **Command** for describing messages routed through the hub.
