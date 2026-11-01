# Builder

A class with chainable methods that collect options and a `build()` that validates and returns an immutable object.

Refs: https://refactoring.guru/design-patterns/builder/typescript/example
Example: [examples/builder.ts](../examples/builder.ts)

**Intent** — Construct a complex object step by step, separating assembly from the final representation.

**Problem** — A constructor with many optional parameters is unreadable at the call site, and the object is invalid until all steps are done.

**Applicability** — **Use** when construction has many optional parts, ordering rules, or validation that should run once at the end. **Avoid** a Builder class when an options object literal with defaults fits (`create({ method: "POST", headers })`), checked by an `interface` with optional properties. This is usually enough in TypeScript.

**TypeScript implementation** — `RequestBuilder` keeps state in `#private` fields and returns `this` from each step so chains type-check on subclasses too. `build()` validates and returns a `Object.freeze`d value typed with `readonly` members. `json()` composes other steps. Gotcha: reusing one builder after `build()` shares mutable state, so copy arrays and maps when building.

**Consequences** — Call sites read clearly and invalid objects never escape. You pay with an extra class that mirrors the product's fields.

**Related patterns** — **Factory Method** suffices when one call creates the object; **Composite** trees are often assembled by builders.
