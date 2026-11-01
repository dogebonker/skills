# Prototype

An object exposes `clone()` so new instances start as deep copies of a configured one.

Refs: https://refactoring.guru/design-patterns/prototype/typescript/example
Example: [examples/prototype.ts](../examples/prototype.ts)

**Intent** — Create new objects by copying an existing instance rather than constructing from scratch.

**Problem** — Building a report, form or game unit from zero is costly or repetitive, and you only need small differences from a known-good template.

**Applicability** — **Use** when configured instances are the natural starting point, or the concrete class is unknown to the caller and only `clone()` is known. **Avoid** a `clone()` method when object spread (`{ ...tpl }`) or `structuredClone` covers plain data. Use spread for shallow copies and `structuredClone` for nested data.

**TypeScript implementation** — `Report.clone()` calls `structuredClone(this.data)`, which deep-copies arrays, maps, sets and `Date`. It drops class prototypes and throws a `DataCloneError` on functions, while cycles are fine, so keep cloned state as plain data inside a class wrapper. The example proves independence by mutating the clone's nested array. Gotcha: spread is shallow, so nested arrays are still shared.

**Consequences** — Cheap setup of near-identical objects with no subclass explosion. Cloning cyclic graphs or objects holding functions or handles needs custom code.

**Related patterns** — **Memento** stores a snapshot instead of a template; **Factory Method** builds from nothing instead.
