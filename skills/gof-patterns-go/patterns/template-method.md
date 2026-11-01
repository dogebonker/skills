# Template Method

A function that runs the fixed sequence and takes the varying steps as an interface (composition, not inheritance).

Refs: https://refactoring.guru/design-patterns/template-method/go/example
Example: [examples/template-method.go](../examples/template-method.go)

**Intent** — Define the skeleton of an algorithm in one place and let variants supply individual steps.

**Problem** — Imports for CSV and logs both read, transform and write, and only the middle details differ.

**Applicability** — **Use** when the sequence must stay identical while one or more steps differ per variant. **Avoid** a steps interface when one function with a func parameter fits or the steps never vary: pass the varying step as a function.

**Go implementation** — Go has no inheritance, so there is no overriding of a base class method. Write `Run(s Steps)` as the skeleton and implement `Steps` in each variant, as `csvImport` does. To share defaults, embed a `base` struct that provides default methods and override only the ones that differ (`logImport` embeds `base`). Gotcha: embedding does not give the base access to the outer type's overrides; the skeleton must call through the interface, which is why `Run` is a separate function.

**Consequences** — One place enforces the algorithm order. The cost is an interface with several methods and embedding that can confuse readers.

**Related patterns** — **Strategy** swaps the whole algorithm instead of its steps; **Factory Method** is often one step of a template; **Decorator** adds behavior around a whole call.
