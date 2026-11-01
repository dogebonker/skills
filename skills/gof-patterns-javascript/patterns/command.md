# Command

Turns an action into a value with `execute` and `undo` closures that can be stored, queued, logged and replayed.

Refs: https://github.com/HowProgrammingWorks/Command  
Example: [examples/command.js](../examples/command.js)

**Intent** — Encapsulate a request as an object so it can be parameterized, queued, logged, or undone.

**Problem** — The caller that triggers an action (button, API, scheduler) should not know how it is done, and some actions need undo or deferred execution.

**Applicability** — **Use** for undo/redo, job queues, macros and audit logs. **Avoid** a command object when nothing is queued, logged or undone: passing the function itself is enough.

**JS implementation** — A command is an object `{ execute, undo }` built by a closure factory (`createCommand`, `append`); the receiver (`Editor`) keeps the history stack in a private field. Returning promises from `execute` gives async commands for free. Gotcha: capture the state needed for undo inside `execute`, just before changing the receiver, otherwise a command queued and run later undoes to stale state.

**Consequences** — Undo, queues and logging come cheap; every undoable action needs a correct inverse, and history grows without a limit unless you cap it.

**Related patterns** — **Memento** undoes by restoring a snapshot instead of an inverse; **Chain of Responsibility** passes a command through handlers; **Strategy** for a function that is chosen, not recorded.
