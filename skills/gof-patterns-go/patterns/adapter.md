# Adapter

A small wrapper type, or a function type with a method, that converts one API shape to another.

Refs: https://refactoring.guru/design-patterns/adapter/go/example
Example: [examples/adapter.go](../examples/adapter.go)

**Intent** — Let code written against one interface use a type that has an incompatible API.

**Problem** — A third-party audit library exposes `WriteEntry(level, text)` but your code expects `Log(msg)`, and you cannot change the library.

**Applicability** — **Use** when you integrate legacy or external code and want to keep your own interface clean. **Avoid** an adapter type when the source already satisfies the interface: Go interfaces are implicit, so nothing more is needed, and changing the source type is simpler still.

**Go implementation** — Write a struct holding the foreign value and implement your consumer-side interface by translating calls, as `auditAdapter` does. For one-method interfaces, a function type with a method (`LoggerFunc`, like `http.HandlerFunc`) adapts any function. Define the target interface in the consumer package, not next to the adapted type. Embedding the adaptee can forward unchanged methods, but wrapping with a named field keeps the surface explicit.

**Consequences** — Isolates foreign APIs behind your interface. The cost is a thin extra type and one more hop per call.

**Related patterns** — **Decorator** keeps the same interface and adds behavior; **Proxy** keeps the same interface and controls access; **Facade** simplifies several APIs rather than converting one.
