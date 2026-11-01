# Strategy

Swaps an algorithm at runtime; in JavaScript a function stored in an object or `Map` and selected by key.

Refs: https://github.com/HowProgrammingWorks/Strategy  
Example: [examples/strategy.js](../examples/strategy.js)

**Intent** — Define a family of interchangeable algorithms and let the caller pick one without changing the code that uses it.

**Problem** — A `switch` on a type or mode grows with every new variant (shipping, pricing, sorting, formatting).

**Applicability** — **Use** when the variant is chosen from input or config. **Avoid** Strategy classes with a single method: a function in a lookup object is enough.

**JS implementation** — `shipping` is an object of functions with a shared signature `(weight) => cost`; `shippingCost` looks up the key and throws on an unknown one, so a typo does not become `undefined is not a function`. Callbacks like `array.sort(compare)` are already strategies. Gotcha: a bare `shipping[method]` also finds `toString` and `__proto__`, so guard keys from input with `Object.hasOwn` or use a `Map`.

**Consequences** — New variants are one entry and each is testable alone; callers must know the available keys, and all strategies need the same signature.

**Related patterns** — **State** for an object that switches its own algorithm; **Factory Method** for a registry that creates objects instead of calling functions; **Template Method** for varying steps of a fixed skeleton.
