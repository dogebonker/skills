# Command

An object with `execute` and `undo` represents an action, so you can queue it, log it, or reverse it; a plain lambda is enough when you need neither undo nor data.

Refs: https://refactoring.guru/design-patterns/command/java/example
Example: [examples/command.kt](../examples/command.kt)

**Intent** — Turn a request into an object so it can be stored, passed, queued and undone.

**Problem** — An editor needs undo. The UI should not know how each action changes the document.

**Applicability** — **Use** when you need undo or redo, queues, logging, retries or macro recording of operations. **Avoid** command classes when you only run code later or the set of actions is closed: `() -> Unit`, `Runnable`, or a sealed class with a `when` reducer is enough.

**Kotlin implementation** — `Command` has `execute()` and `undo()`. `AppendText` and `Clear` hold their receiver and the data needed to undo. `History` keeps an `ArrayDeque` and pops with `removeLastOrNull`. Commands that need state to undo, like `Clear`, capture it in `execute`. Android examples: `Intent` describes an action to run, `Runnable` posted to a `Handler`, and Navigation `NavDirections` are command-like. Gotcha: undo must restore the exact prior state, so test the round trip.

**Consequences** — Undo, queues and logging come naturally. There is one class per action unless you use lambdas.

**Related patterns** — **Memento** stores state to undo instead of reversing the action; **Strategy** is an algorithm object, not a request; **Chain of Responsibility** routes a command.
