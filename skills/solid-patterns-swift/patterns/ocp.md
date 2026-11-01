# Open/Closed (OCP)

Add new behavior by adding code, not by editing code that already works.

Refs: https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html, https://docs.swift.org/swift-book/documentation/the-swift-programming-language/protocols/
Example: [examples/ocp.swift](../examples/ocp.swift)

**Principle** — A module should be extensible without being modified; Martin's 1996 paper adds that closure is always partial, so aim it at the changes most likely to come. Swift gives two strong tools: protocols, which any type can adopt, and extensions, which add a conformance to a type you do not own without touching its source (retroactive conformance; a foreign type to a foreign protocol needs `@retroactive` in Swift 6).

**Violation signals** — A `switch` on a string or raw value that gains a case per feature, as `trackV1` does. `if let x = y as? ConcreteType` chains choosing behavior. The same enum switched in many files when cases are added often.

**Fix** — Declare `AnalyticsSink`, make `Tracker` hold `[any AnalyticsSink]`, and add destinations as new types (`ConsoleSink`) or as an `extension WarehouseClient: AnalyticsSink`. `Tracker` never changes. Use `some AnalyticsSink` instead of `any` when one concrete type is known statically.

**When not to apply** — A closed set you own (payment state, sort order) is better as an `enum` with an exhaustive `switch`: adding a case then fails to compile wherever it is unhandled. A protocol nobody else conforms to is ceremony. Wait for the second real variant.

**Related** — **Strategy** (`gof-patterns-swift/patterns/strategy.md`) for swapping one algorithm; **Adapter** (`gof-patterns-swift/patterns/adapter.md`) for the extension that fits `WarehouseClient`; **Decorator** (`gof-patterns-swift/patterns/decorator.md`) for extending by wrapping; **DIP** ([dip.md](dip.md)) for who owns the protocol; **YAGNI** (`kiss-patterns/patterns/yagni.md`) for unused extension points.
