# Builder

Named arguments with defaults replace most builders, and a lambda with receiver gives a type-safe DSL when construction has steps or nesting.

Refs: https://refactoring.guru/design-patterns/builder/java/example
Example: [examples/builder.kt](../examples/builder.kt)

**Intent** — Construct complex objects step by step, with validation, without telescoping constructors.

**Problem** — An `HttpRequest` has many optional parts. Constructors with long positional lists are unreadable and invalid combinations slip through.

**Applicability** — **Use** when construction has steps, nesting, repeated elements (many headers) or validation that needs the full set of inputs. **Avoid** a builder class when optional fields are the only issue: a data class with default values and named arguments, and `copy()` for variants, is enough.

**Kotlin implementation** — Start with `HttpRequest(url = ..., timeoutMs = 2_000)`. When more is needed, write `RequestBuilder` with mutable properties and a `build()` that runs `require(...)`, then expose `fun request(url: String, init: RequestBuilder.() -> Unit)`. `apply(init)` runs the lambda on the builder. Mark DSL builders with `@DslMarker` if you nest them, so inner blocks cannot call outer members. Many Android types follow this: `NotificationCompat.Builder`, `AlertDialog.Builder`, and Compose modifiers. Gotcha: keep the product immutable, with `val` fields, and let only the builder be mutable.

**Consequences** — Call sites read like configuration and invalid objects are rejected in one place. The DSL adds a class and a function that defaults would not need.

**Related patterns** — **Prototype** starts from an existing object and copies it; **Abstract Factory** creates families, not stepwise assembly; **Composite** describes the trees builders often produce.
