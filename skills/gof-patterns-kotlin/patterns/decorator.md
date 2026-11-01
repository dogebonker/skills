# Decorator

A wrapper implements the same interface and forwards to the wrapped object with `by`, overriding only the members it changes.

Refs: https://refactoring.guru/design-patterns/decorator/java/example
Example: [examples/decorator.kt](../examples/decorator.kt)

**Intent** — Add behaviour to an object by wrapping it, without subclassing.

**Problem** — A storage component needs logging, upper-casing or caching in different combinations, which subclasses cannot express without an explosion of classes.

**Applicability** — **Use** when behaviour should be stacked at runtime and each layer follows the same interface. **Avoid** a wrapper class when the extra behaviour is a single hook: a lambda, or an extension function when no state is needed, is enough.

**Kotlin implementation** — `LoggingStorage(inner: Storage) : Storage by inner` forwards every member, and `override fun save` adds the logging before calling `inner.save`. Without `by` you would write every forwarding method by hand. Stack decorators in the constructor: `LoggingStorage(UppercaseStorage(MemoryStorage()))`. Order matters. The delegate must be an interface, because `by` does not work with open classes. Gotcha: delegated members call `inner` directly, so an override in the decorator is not seen when `inner` calls its own methods internally. OkHttp interceptors and `ContextWrapper` follow this shape.

**Consequences** — Flexible, composable behaviour with little code. Many small wrappers can make stack order hard to follow.

**Related patterns** — **Proxy** has the same structure but controls access instead of adding features; **Adapter** changes the interface; **Chain of Responsibility** is also a chain of wrappers.
