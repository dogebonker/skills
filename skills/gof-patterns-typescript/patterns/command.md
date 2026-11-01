# Command

An object (or a function pair) that bundles an action, its data, and optionally how to reverse it.

Refs: https://refactoring.guru/design-patterns/command/typescript/example
Example: [examples/command.ts](../examples/command.ts)

**Intent** — Turn a request into an object so it can be queued, logged, undone or passed around.

**Problem** — An editor needs undo, a job system needs queued actions, and callers should not know how each action works.

**Applicability** — **Use** when you need undo/redo, queues, scheduling, or macros. **Avoid** a Command object when a single callback `() => void` covers fire-and-forget. Use an interface only when you need `undo`, or extra data on the action.

**TypeScript implementation** — `Command` is an interface of `execute` and `undo`; `appendText(doc, added)` is a closure that returns an object literal capturing the receiver and arguments. `Editor` keeps a `#history` stack and `undo()` pops with `?.`. No class per command is needed. Gotcha: record the previous value inside `execute`, not when the command is created, so queued commands undo correctly; computing an inverse (slicing off `added`) breaks on edge cases such as an empty string.

**Consequences** — Decouples invoker from receiver and gives you history. Each action becomes its own small unit to maintain.

**Related patterns** — **Memento** restores state instead of reversing steps; **Chain of Responsibility** routes commands to handlers; **Strategy** swaps algorithms rather than recording actions.
