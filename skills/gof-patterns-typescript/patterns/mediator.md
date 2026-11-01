# Mediator

One object receives messages from participants and routes them, so participants hold a reference only to the mediator.

Refs: https://refactoring.guru/design-patterns/mediator/typescript/example
Example: [examples/mediator.ts](../examples/mediator.ts)

**Intent** — Reduce chaotic many-to-many dependencies by forcing communication through a central object.

**Problem** — Chat users, form widgets or UI panels that each know all the others become tangled and hard to change.

**Applicability** — **Use** when components are tightly coupled through direct references and you want to reuse them separately. **Avoid** a Mediator class when components only announce events and need no coordinated logic: an event emitter (Observer) is enough.

**TypeScript implementation** — `ChatRoom` keeps a `Set<Participant>` in a `#private` field and `broadcast` skips the sender. `User` depends on the room, not on other users. Define the participant contract as an `interface` so the mediator does not import concrete classes. Gotcha: the mediator tends to absorb all logic and become a god object, so keep it to routing and coordination.

**Consequences** — Loose coupling and one place to read the interaction rules. The mediator itself can grow complex.

**Related patterns** — **Observer** handles one-way notification; **Facade** simplifies without peer coordination; **Command** can be the messages routed.
