# Mediator

A central object receives messages from participants and forwards them, so participants only know the mediator.

Refs: https://refactoring.guru/design-patterns/mediator/java/example
Example: [examples/mediator.kt](../examples/mediator.kt)

**Intent** — Reduce direct dependencies between objects by making them talk through a coordinator.

**Problem** — Chat users or screen widgets that reference each other directly create a tangle that is hard to change.

**Applicability** — **Use** when many objects interact in complex ways and you want to change the interaction in one place. **Avoid** a hand-built mediator when only two objects interact or the coordination is UI state: one object calling the other, or a ViewModel with `StateFlow`, is enough.

**Kotlin implementation** — `ChatRoom` implements `Room`. `User` holds a `Room`, and `say` calls `room.broadcast(this, text)`. Members never hold other members. Pass the mediator as an interface so participants stay testable. A ViewModel is the Android mediator between UI and data: screens send events to it and observe its state, and never talk to each other. `NavController` mediates navigation between destinations, and an `EventBus`-style shared flow is a looser form. Gotcha: the mediator can grow into a god class, so split by feature.

**Consequences** — Participants become reusable and interaction logic lives in one place. The mediator can become a bottleneck of complexity.

**Related patterns** — **Observer** notifies one way, with no central logic; **Facade** is a one-way simplified entry point; **Command** can carry the messages through the mediator.
