# Mediator

A struct that owns the participants and routes messages by id, so peers hold no references to each other.

Refs: https://refactoring.guru/design-patterns/mediator/rust/example
Example: [examples/mediator.rs](../examples/mediator.rs)

**Intent** — Replace direct many-to-many links with a central coordinator.

**Problem** — Chat users should not hold references to every other user.

**Applicability** — **Use** when peers are tightly coupled by direct calls, and changing one forces changes in others. **Avoid** a mediator struct when two objects talk: a direct method call is enough, and across threads an `mpsc` channel is the idiomatic mediator.

**Rust implementation** — `ChatRoom` owns `Vec<User>`; `join` returns an index, and `say(from, text)` pushes into the other users' inboxes. Participants hold an id, not a reference, so there is no `Rc<RefCell<..>>` cycle. Use `Rc<RefCell<Mediator>>` with `Weak` back-references only when participants must call the mediator on their own initiative. The gotcha: iterating `self.users.iter_mut()` while also reading `self.users[from]` would conflict, so compute what you need (the formatted line) before the loop.

**Consequences** — Peers become independent and interactions live in one place. The cost is a mediator that grows complex.

**Related patterns** — **Observer** is one-way broadcast, where a mediator is two-way; **Facade** simplifies but does not coordinate peers; **Command** for messages as objects.
