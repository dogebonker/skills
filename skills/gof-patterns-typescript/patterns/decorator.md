# Decorator

A higher-order function takes a function (or object) and returns one with the same type plus extra behaviour.

Refs: https://refactoring.guru/design-patterns/decorator/typescript/example
Example: [examples/decorator.ts](../examples/decorator.ts)

**Intent** — Add responsibilities to an object dynamically by wrapping it in an object with the same interface.

**Problem** — You want logging, retry, caching or auth around a call, in any combination, without a subclass for each mix.

**Applicability** — **Use** when behaviour must be stacked at runtime and the wrapped thing has a stable interface. **Avoid** decorator classes when a function type makes wrappers one-liners (`withLogging(fn)`): higher-order functions are enough. TypeScript 5+ standard `@decorator` syntax applies only to classes and class members, so higher-order functions are the idiom for plain functions.

**TypeScript implementation** — `type Fetcher = (url: string) => Promise<string>` is the shared signature. `withLogging` and `withRetry(3)` take a `Fetcher` and return a `Fetcher`, so they nest: `withLogging(withRetry(3)(flaky))`. Order matters: retry inside logging logs once. For object interfaces implement the same `interface` and hold the inner object in a `#private` field. Gotcha: wrappers hide extra members of the inner type.

**Consequences** — Composable behaviours without class explosion. Deep stacks are hard to debug and order-sensitive.

**Related patterns** — **Proxy** controls access rather than adding features; **Chain of Responsibility** lets a handler stop the call; **Strategy** swaps behaviour rather than wrapping it.
