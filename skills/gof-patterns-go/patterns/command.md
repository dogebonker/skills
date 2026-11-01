# Command

A struct of function values (`Do`, `Undo`) that closes over the receiver and its arguments.

Refs: https://refactoring.guru/design-patterns/command/go/example
Example: [examples/command.go](../examples/command.go)

**Intent** — Turn an action into an object so it can be passed around, queued, recorded or reversed.

**Problem** — An editor needs undo, and operations must be recorded as values rather than executed immediately.

**Applicability** — **Use** when you need history, undo/redo, deferred execution, retries or macro recording. **Avoid** command structs when there is no undo or metadata: a plain function or method value (`ed.Save`) is enough.

**Go implementation** — Use closures: `Editor.Append` returns a `Command` whose `Do` and `Undo` capture the editor and text, as in the example. If there is no undo, a `func()` is the whole pattern. If commands need to be serialized, use a struct with data fields and a separate executor instead of closures. Keep a slice as the history stack. Gotcha: `Undo` must account for later state changes, so capture only what is needed to reverse this step.

**Consequences** — Actions become values you can queue and replay. The cost is capturing enough state to reverse each command.

**Related patterns** — **Memento** stores state snapshots for undo instead of inverse operations; **Strategy** also uses function values but selects an algorithm; **Chain of Responsibility** routes commands to handlers.
