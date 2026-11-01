# Adapter

An extension function or small wrapper class makes a type you cannot change satisfy the interface your code expects.

Refs: https://refactoring.guru/design-patterns/adapter/java/example
Example: [examples/adapter.kt](../examples/adapter.kt)

**Intent** — Let code written against one interface use a class with an incompatible interface.

**Problem** — A vendor SDK exposes `dispatch(number: String, body: ByteArray)` but the app talks to a `MessageSender` with strings.

**Applicability** — **Use** when you integrate a library, legacy class or platform API whose shape differs from your own interface. **Avoid** a wrapper type when only a conversion is needed: an extension function (`fun Dto.toModel()`) or a mapper function is enough.

**Kotlin implementation** — Write `fun LegacySmsGateway.asSender(): MessageSender = object : MessageSender { ... }`. The adapter translates the arguments and the result code, and returns `false` when the phone has no digits. It passes the digits as a string, because a `Long` would drop leading zeros. Extension functions keep the adapter next to the adapted type and read well at the call site. Use a class when the adapter keeps state. `RecyclerView.Adapter` is the Android version: it adapts your data list to the views the RecyclerView expects, and `ListAdapter` with `DiffUtil` adds diffing. Gotcha: do not leak the adaptee's types through the target interface.

**Consequences** — Your code stays free of vendor types and the adapter is easy to test. It adds a thin layer to maintain.

**Related patterns** — **Decorator** keeps the interface and adds behaviour; **Facade** simplifies a whole subsystem; **Proxy** keeps the same interface and controls access.
