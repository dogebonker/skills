# Mediator

A central object handles communication between peers, so they reference only the mediator.

Refs: https://refactoring.guru/design-patterns/mediator/python/example
Example: [examples/mediator.py](../examples/mediator.py)

**Intent** — Reduce many-to-many dependencies between objects by routing them through one coordinator.

**Problem** — Chat users that hold references to each other become tangled and hard to change.

**Applicability** — **Use** when a group of objects interacts in complex ways and you want that logic in one place. **Avoid** a Mediator class when one-way notification fits: Observer or a callback is lighter, and an `asyncio.Queue` or message bus can replace a bespoke mediator.

**Python implementation** — `ChatRoom` keeps `_users: dict[str, User]`, `join` sets `user.room`, and `send` delivers to a target or everyone else. `User.say` calls the room, and the room calls `receive`. Both sides hold a reference to the other, so use type annotations with `from __future__ import annotations` for forward references. Gotcha: the mediator can turn into a god object; keep it limited to routing and coordination.

**Consequences** — Peers are reusable and interactions are visible in one class. Cost: the mediator concentrates complexity.

**Related patterns** — **Observer** is how the mediator is often notified; **Facade** simplifies without peer communication; **Command** can be the message format.
