# Adapter

A small class that implements the interface your code expects and translates each call to an incompatible existing API.

Refs: https://refactoring.guru/design-patterns/adapter/typescript/example
Example: [examples/adapter.ts](../examples/adapter.ts)

**Intent** — Let objects with incompatible interfaces work together by converting one interface to another.

**Problem** — A legacy or third-party gateway takes dollars as strings and returns status codes, while your code speaks cents and booleans.

**Applicability** — **Use** when you must reuse a class whose interface does not match, and you cannot or should not edit it. **Avoid** an Adapter class when the shapes are already structurally compatible (TypeScript accepts it as is): a single mapping function `(x: Legacy) => Modern` is enough.

**TypeScript implementation** — `LegacyGatewayAdapter implements PaymentProcessor` holds the gateway in a `#private` field and converts units and result shape inside `pay`. Callers only see `PaymentProcessor`. Structural typing means no inheritance is needed and mocks are trivial object literals. Gotcha: keep the adapter thin; business rules inside it belong elsewhere.

**Consequences** — Isolates third-party shapes at one seam and keeps the core clean. It adds one more type per integration.

**Related patterns** — **Facade** simplifies instead of converting; **Decorator** keeps the interface and adds behaviour; **Proxy** keeps the interface and controls access.
