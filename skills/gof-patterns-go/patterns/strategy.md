# Strategy

A function type, with the strategies as plain functions or closures.

Refs: https://refactoring.guru/design-patterns/strategy/go/example
Example: [examples/strategy.go](../examples/strategy.go)

**Intent** — Define a family of interchangeable algorithms and let the caller pick one.

**Problem** — Cart totals depend on a pricing rule (regular, sale, loyalty discount) chosen per customer or campaign.

**Applicability** — **Use** when several variants of one operation exist and the choice varies at runtime. **Avoid** a strategy interface when only one algorithm is used: call it directly, since a one-method interface with one implementation adds nothing.

**Go implementation** — Declare `type Pricing func(float64) float64`, pass it to `total`, and register named functions in a map, as in the example. Closures like `Loyalty(pct)` carry configuration. Use a one-method interface only when strategies need state or several methods; `sort.Slice` and `slices.SortFunc` take their comparison as a function for the same reason. Gotcha: a nil function panics when called, so default it or validate at the boundary.

**Consequences** — Easy swapping and testing with very little code. The cost is that the caller must know enough to choose.

**Related patterns** — **State** lets the object itself change the algorithm; **Template Method** fixes the skeleton and varies steps; **Command** wraps an action with undo and data.
