# Mediator

Routes communication between peers through one object so that they never reference each other; in JavaScript a class or closure holding a registry of callbacks.

Refs: https://github.com/HowProgrammingWorks/Mediator  
Example: [examples/mediator.js](../examples/mediator.js)

**Intent** — Centralize the rules of how a group of objects interact and reduce many-to-many coupling to many-to-one.

**Problem** — Components such as chat users, form fields or services call each other directly, so each change ripples through all of them.

**Applicability** — **Use** when interaction rules (routing, ordering, permissions) belong in one place. **Avoid** a mediator when peers only announce facts: an `EventEmitter` is enough.

**JS implementation** — `ChatRoom` stores handlers in a `Map` and returns a `say` function from `join`, so a participant holds a capability instead of a reference to the room's internals. `#broadcast` is private and skips the sender. Components get the mediator by injection, not by import. Keep the mediator to routing; domain logic inside it turns it into a god object. Gotcha: `join` with a name already in the room replaces the earlier handler, so check the name first when names come from users.

**Consequences** — Peers become reusable and the protocol is readable in one file; the mediator can grow into a bottleneck and a single point of failure.

**Related patterns** — **Observer** for one-way notification with no routing rules; **Facade** for a one-way simplified API; **Command** for the messages it routes.
