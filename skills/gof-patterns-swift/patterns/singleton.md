# Singleton

One shared instance exposed as `static let shared`, which Swift initializes lazily and thread-safely.

Refs: https://refactoring.guru/design-patterns/singleton/swift/example
Example: [examples/singleton.swift](../examples/singleton.swift)

**Intent** — Ensure a type has a single instance and give a global access point to it.

**Problem** — A resource such as configuration, a log sink, or a connection pool must exist once for the whole process.

**Applicability** — **Use** when exactly one instance is a real invariant of the system and the shared state is protected by isolation. **Avoid** a `static let shared` singleton when the instance is only convenient: an `init` parameter is enough, and tests can pass a fresh instance. Hidden globals make code hard to test.

**Swift implementation** — Write `static let shared = AppConfiguration()` with a `private init()`. In Swift 6 a shared mutable instance must be `Sendable`: make it an `actor` (as the example does), a `@MainActor` type, or a final class with a lock and `Sendable`. A `static var` is a data-race error in Swift 6 mode. The example also shows `Reporter` receiving the instance by parameter, which is usually the better design.

**Consequences** — Convenient access and one initialization point. It adds hidden coupling, hurts testing, and an actor singleton forces `await` at each call.

**Related patterns** — **Abstract Factory** and **Facade** are often exposed as singletons; **Flyweight** keeps many shared instances; **State** can share its state objects.
