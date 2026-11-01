# Singleton

An `object` declaration creates one instance, initialised lazily and thread-safely, but on Android a DI-scoped single instance is the default choice.

Refs: https://refactoring.guru/design-patterns/singleton/java/example
Example: [examples/singleton.kt](../examples/singleton.kt)

**Intent** — Ensure there is one instance of a type and give a global access point to it.

**Problem** — A resource such as configuration or a connection pool must exist once per process.

**Applicability** — **Use** when exactly one instance is a real requirement and it has no per-test or per-user variation. **Avoid** an `object` singleton when it holds state that tests or features need to replace: a normal class provided by Hilt with `@Singleton`, or constructor injection, is enough. A top-level `val` or constant also works for plain values.

**Kotlin implementation** — Write `object PaymentConfig { ... }`. The JVM initialises it on first access, and the class loader guarantees thread safety, so you need no double-checked locking. `init` runs once. Objects cannot take constructor arguments, which is why Android code that needs a `Context` uses `@Singleton` with `@Inject constructor` instead. The example's `Clock` is a plain class with an injectable time source, which a test can fake. Gotchas: an `object` holding an Activity or Context leaks it, and mutable fields need their own thread safety, which is why the example marks `record` and `history` `@Synchronized` and bounds `callLog`.

**Consequences** — Simple access and safe initialisation. The cost is hidden global state that makes tests and modules harder to isolate.

**Related patterns** — **Facade** is often a Kotlin `object`; **Flyweight** shares instances through a factory; **Abstract Factory** is commonly a single instance.
