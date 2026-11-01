# Singleton

A module-level `export const`, since ES modules are evaluated once, with a class using `#instance` only when creation must be lazy.

Refs: https://refactoring.guru/design-patterns/singleton/typescript/example
Example: [examples/singleton.ts](../examples/singleton.ts)

**Intent** — Guarantee a single instance and provide one global access point.

**Problem** — Several parts of a program need to share one resource such as configuration, a connection pool or a logger, and duplicates would be wrong.

**Applicability** — **Use** when exactly one instance must exist and must be shared by many callers. **Avoid** a Singleton class when an ES module does it already: `export const settings = Object.freeze({...})`. Prefer that, or pass the instance as an argument.

**TypeScript implementation** — The module cache makes any exported value a singleton, so no class is needed. For lazy creation use `static #instance` with `??=` in a static getter and a `private constructor`. `private` only blocks `new` at compile time, so use `#` fields for runtime privacy. Gotcha: tests share the instance, and bundlers or dual CJS/ESM loads can create two copies.

**Consequences** — Simple shared access and lazy creation. It is global state, which hides dependencies and makes tests order-dependent.

**Related patterns** — **Facade** is often exposed as a singleton; **Flyweight** shares many small objects instead of one.
