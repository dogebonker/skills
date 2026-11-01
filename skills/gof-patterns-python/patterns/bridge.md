# Bridge

Split an abstraction from its implementation and join them with a reference, so each side varies on its own.

Refs: https://refactoring.guru/design-patterns/bridge/python/example
Example: [examples/bridge.py](../examples/bridge.py)

**Intent** — Avoid a class explosion when two dimensions vary independently, such as report type and output destination.

**Problem** — `ConsoleTotalReport`, `FileTotalReport`, `ConsoleDetailReport`, and so on multiply with every new option.

**Applicability** — **Use** when you have two orthogonal axes of variation and want to combine them at runtime. **Avoid** a Bridge class hierarchy when one axis has a single value, or when passing a function (`Callable[[str], None]`) as the implementation is enough.

**Python implementation** — `Report` is the abstraction and keeps a `Sink` Protocol reference in `self.sink`. `TotalReport` and `DetailReport` refine the abstraction; `ConsoleSink` and `ListSink` implement the other side. Any object with `write(text)` qualifies, with no inheritance. Gotcha: the abstraction should delegate work to the sink, not inspect its concrete type.

**Consequences** — New reports and new sinks are added independently, and sinks can be swapped at runtime. Cost: more indirection than a single class.

**Related patterns** — **Adapter** retrofits compatibility; **Strategy** is structurally close but about swapping algorithms; **Abstract Factory** can create the matching bridge halves.
