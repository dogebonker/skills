# Factory Method

A constructor function that returns an interface, choosing the concrete type from its arguments.

Refs: https://refactoring.guru/design-patterns/factory-method/go/example
Example: [examples/factory-method.go](../examples/factory-method.go)

**Intent** — Move the decision about which concrete type to build into one function, so callers depend only on an interface.

**Problem** — Code scatters `if kind == ...` branches and concrete struct literals, so adding a new kind means editing every caller.

**Applicability** — **Use** when the concrete type depends on runtime input such as config, a flag or a payload, and callers should not care which one they get. **Avoid** a factory interface when the type is known at compile time or has one implementation: return the struct from a plain `NewX` constructor.

**Go implementation** — Name it `NewX` and return an interface plus an `error` for unknown kinds, as `NewNotifier` does. Define the interface (`Notifier`) next to the consumer, keep concrete types (`emailNotifier`) unexported, and use a `map[string]func() T` registry when kinds are added from other packages. Go has no subclass overriding, so the classic creator hierarchy collapses into one function. Gotcha: returning a nil concrete pointer as an interface gives a non-nil interface; return an untyped `nil` on error.

**Consequences** — Callers decouple from concrete types and new kinds touch one place. The cost is an interface plus a switch that must stay in sync with the types.

**Related patterns** — **Abstract Factory** for several related products created together; **Strategy** for a choice of behavior rather than construction.
