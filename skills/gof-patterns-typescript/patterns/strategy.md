# Strategy

A function type is the interface, and each algorithm is a function you pass in or swap at runtime.

Refs: https://refactoring.guru/design-patterns/strategy/typescript/example
Example: [examples/strategy.ts](../examples/strategy.ts)

**Intent** — Define a family of interchangeable algorithms and let the client choose one.

**Problem** — Shipping cost is computed by flat rate, weight, or free-over-threshold, and `if/else` on a mode flag keeps growing.

**Applicability** — **Use** when several variants of one algorithm exist and you want to pick or change them at runtime. **Avoid** a Strategy interface and class hierarchy when a function type is enough: `type ShippingStrategy = (kg: number) => number`.

**TypeScript implementation** — The three strategies are plain arrow functions collected in a record checked with `satisfies Record<string, ShippingStrategy>`, which keeps the literal keys. `Cart` holds one in a `#private` field and calls it. Closures configure a strategy: `perKilo(rate)` can return the function. Use a class only if a strategy needs state or several methods. Gotcha: typing strategies as `Function` loses type safety.

**Consequences** — Removes conditionals and makes algorithms testable alone. Clients must know the options to choose one.

**Related patterns** — **State** lets the object pick the strategy itself; **Template Method** varies steps through inheritance; **Command** wraps an action with data.
