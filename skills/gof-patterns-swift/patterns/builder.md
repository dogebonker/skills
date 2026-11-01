# Builder

A value type that accumulates configuration step by step and produces an immutable result with `build()`.

Refs: https://refactoring.guru/design-patterns/builder/swift/example
Example: [examples/builder.swift](../examples/builder.swift)

**Intent** — Separate construction of a complex object from its representation so the same steps can build different configurations.

**Problem** — An initializer with many optional parameters becomes unreadable and callers must remember argument order.

**Applicability** — **Use** when an object has many optional parts, construction needs validation or ordering, or you want fluent call sites. **Avoid** a builder type when default arguments and memberwise `init` cover the options: Swift's default parameter values are enough.

**Swift implementation** — Make the builder a struct whose steps return a modified copy (`func header(_:_:) -> Self`), as `HTTPRequestBuilder` does, so chains need no `var` and no reference semantics. `build()` returns the immutable `HTTPRequest`. For declarative UI trees use `@resultBuilder`, which is Swift's built-in builder syntax (SwiftUI's `ViewBuilder`). Avoid `@discardableResult` mutating builders that hide misuse.

**Consequences** — Readable call sites and one validation point. It adds a parallel type to maintain whenever the product gains a field.

**Related patterns** — **Abstract Factory** for building a whole family in each step; **Composite** is a common builder output, since builders often assemble trees; **Prototype** for starting from an existing configuration.
