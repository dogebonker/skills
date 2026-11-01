# Command

A struct holding boxed closures for do and undo, kept in a `Vec` history.

Refs: https://refactoring.guru/design-patterns/command/rust/example
Example: [examples/command.rs](../examples/command.rs)

**Intent** — Package an operation and what it needs so it can be executed now or later and reversed.

**Problem** — An editor needs undo, and each action must remember how to reverse itself.

**Applicability** — **Use** when you queue, log, schedule or undo operations. **Avoid** a Command struct when there is no undo or inspection: pass a closure.

**Rust implementation** — `Command { label, run: Box<dyn Fn(&mut Vec<String>)>, undo: ... }`. A constructor like `append_line(text)` captures its data with `move` closures. The `Editor` owns the document and a `Vec<Command>` history; `execute` runs and pushes, `undo` pops and calls the undo closure. Commands receive the document (`&mut Vec<String>`) as an argument rather than capturing it, which sidesteps the borrow checker problem of a closure holding a mutable borrow of the receiver for its whole life. If commands are a closed set, an enum with `apply` and `revert` methods is simpler and printable.

**Consequences** — Undo, queues and logging come cheaply. The cost is boxing and a command per action.

**Related patterns** — **Memento** stores snapshots instead of inverse operations; **Strategy** holds interchangeable algorithms, not queued actions; **Chain of Responsibility** passes requests along handlers.
