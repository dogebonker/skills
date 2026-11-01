# Dependency Inversion (DIP)

High-level policy should not depend on low-level details; both depend on an abstraction the policy owns.

Refs: https://cs.utexas.edu/~downing/papers/DIP-1996.pdf
Example: [examples/dip.kt](../examples/dip.kt)

**Principle** — Martin states two rules: high-level modules do not depend on low-level modules, and abstractions do not depend on details. The policy declares the interface and the detail conforms. On Android the guide recommends constructor injection and Hilt (https://developer.android.com/training/dependency-injection/hilt-android): an `@Inject` constructor takes the interface, and a `@Module` with `@Binds` maps it to the implementation.

**Violation signals** — `SmsGateway()`, `Retrofit.Builder()` or `Room.databaseBuilder(...)` called inside a ViewModel or domain class (`OrderServiceV1`). Access through a global `object` instead of a constructor parameter. Tests that need a mocking library or reflection to replace a dependency.

**Fix** — `OrderService` takes a `fun interface OrderNotifier` in its constructor. `SmsOrderNotifier` adapts the concrete `SmsGateway`, and only `main` (on Android, the Hilt graph) builds it. A test passes a lambda that records messages; the Android guide prefers such fakes to mocks.

**When not to apply** — An interface with one implementation and no fake is ceremony; a class with an `@Inject` constructor can be injected directly without an interface or `@Binds`. Do not hide stable stdlib or pure helpers behind ports. A Hilt module for a two-class console tool is more setup than the tool.

**Related** — **Adapter** (`gof-patterns-kotlin/patterns/adapter.md`), as `SmsOrderNotifier` shows; **Strategy** (`gof-patterns-kotlin/patterns/strategy.md`) for an injected function; **Abstract Factory** (`gof-patterns-kotlin/patterns/abstract-factory.md`); **Singleton** (`gof-patterns-kotlin/patterns/singleton.md`), which a DI scope replaces; **ISP** ([isp.md](isp.md)); **Pattern overuse** (`kiss-patterns/patterns/pattern-overuse.md`).
