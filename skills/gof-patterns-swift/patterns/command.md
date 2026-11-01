# Command

A value that bundles an action and its undo as closures, so operations can be queued, logged and reversed.

Refs: https://refactoring.guru/design-patterns/command/swift/example
Example: [examples/command.swift](../examples/command.swift)

**Intent** — Turn a request into a standalone object so it can be stored, passed, scheduled, or undone.

**Problem** — A thermostat or editor needs undo and a history of operations that UI controls trigger.

**Applicability** — **Use** when you need undo/redo, queuing, macros, or to decouple the invoker from the receiver. **Avoid** a one-method command class when you just call a function once: a closure is enough.

**Swift implementation** — Use a struct `Command` with `execute` and `undo` closures and a factory function whose `execute` records the previous state when it runs, as `setTarget(_:on:)` does, so commands queued and run later still undo correctly. `CommandHistory` keeps an array and pops to undo. Mark closures `@Sendable` if commands cross concurrency domains. Stored closures that capture `self` strongly create retain cycles, so capture the receiver explicitly. If the receiver can own the history, capture it `[weak receiver]`. `UndoManager` in Foundation is the platform command stack.

**Consequences** — Undo, queues and logs become easy. State capture must be done carefully, and many tiny commands add overhead.

**Related patterns** — **Memento** stores state for undo; **Chain of Responsibility** can dispatch commands; **Strategy** also stores behavior in a closure, but chooses how a job is done rather than recording an action; **Observer** notifies after execution.
