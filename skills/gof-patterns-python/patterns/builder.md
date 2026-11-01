# Builder

A builder collects options step by step and produces a validated, usually immutable, object from `build()`.

Refs: https://refactoring.guru/design-patterns/builder/python/example
Example: [examples/builder.py](../examples/builder.py)

**Intent** — Separate construction of a complex object from its representation, so one construction process yields differently configured results.

**Problem** — A request with many optional parts and cross-field rules is awkward to create with one huge constructor.

**Applicability** — **Use** when construction has many steps, must be validated as a whole, or must produce several representations. **Avoid** a Builder class when keyword arguments with defaults do the job: a `@dataclass` with defaults and `dataclasses.replace` covers most Python cases without any builder.

**Python implementation** — The product `HttpRequest` is a `@dataclass(frozen=True)`. `RequestBuilder` keeps mutable private fields, each setter returns `self` for chaining, and `build()` validates (`url` required) and copies the headers dict so later builder changes cannot leak into the product. Return type annotations use `from __future__ import annotations` so the class can name itself on 3.10. Gotcha: copy mutable fields in `build()`.

**Consequences** — Readable construction and one place for validation. Cost: a second class to maintain; skip it when defaults suffice, as the demo's last line shows.

**Related patterns** — **Abstract Factory** and **Prototype** also build objects but in one call; **Composite** trees are commonly assembled by builders.
