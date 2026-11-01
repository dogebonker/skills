# Decorator

A function that takes a value of an interface and returns another value of the same interface, such as HTTP middleware.

Refs: https://refactoring.guru/design-patterns/decorator/go/example
Example: [examples/decorator.go](../examples/decorator.go)

**Intent** — Attach extra responsibilities to an object by wrapping it in another object with the same interface.

**Problem** — Handlers need logging, auth and rate limiting in varying combinations, and subclassing for each combination is impossible in Go anyway.

**Applicability** — **Use** when behavior must be layered or reordered per use, and the wrapped and wrapper share an interface. **Avoid** a wrapper type when you own the type and the behavior is always on: put it in the type, since embedding alone already promotes every method.

**Go implementation** — Define `type Middleware func(http.Handler) http.Handler`, write wrappers like `logging` and `requireToken`, and compose them with `chain`, which applies the list so the first entry runs outermost. The same shape works for any interface: `io.Reader` wrappers (`bufio`, `gzip`) are decorators. For wide interfaces, embed the interface in a struct and override only the methods you change. Order matters: auth before logging versus after gives different logs.

**Consequences** — Behavior composes freely and stays testable in isolation. The cost is many small wrappers and stack traces that pass through each layer.

**Related patterns** — **Proxy** has the same shape but access control as the goal; **Chain of Responsibility** lets a layer stop the request; **Adapter** changes the interface instead of keeping it.
