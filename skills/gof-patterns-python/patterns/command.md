# Command

A request becomes an object (or callable) that can be queued, logged, executed and undone.

Refs: https://refactoring.guru/design-patterns/command/python/example
Example: [examples/command.py](../examples/command.py)

**Intent** — Encapsulate an action with its parameters so it can be passed around and reversed.

**Problem** — A UI button, a job queue and an undo stack all need to trigger operations without knowing their details.

**Applicability** — **Use** when you need undo/redo, queuing, scheduling or an audit log. **Avoid** a Command class when you only need to run something later: a plain function, lambda or `functools.partial` is already a command (the demo's last lines).

**Python implementation** — `Command` is a Protocol with `execute()` and `undo()`. `AddItem` is a `@dataclass` that stores its receiver (`cart`) and arguments (`item`). `History.run` executes and records; `undo` pops and reverses. Gotcha: `undo` must restore exact prior state, so capture what you need at execute time (for example an index or removed value) rather than recomputing it.

**Consequences** — Decouples invoker from receiver, enables undo and queues. Cost: one class per operation when undo is needed.

**Related patterns** — **Memento** can store state for undo; **Chain of Responsibility** passes commands along; **Strategy** also encapsulates behavior but chooses how rather than what to do; **Observer** may trigger commands.
