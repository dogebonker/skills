# Template Method

An abstract base class defines the algorithm's skeleton in a public method and leaves abstract or overridable steps to subclasses.

Refs: https://refactoring.guru/design-patterns/template-method/typescript/example
Example: [examples/template-method.ts](../examples/template-method.ts)

**Intent** — Define the skeleton of an algorithm and let subclasses redefine certain steps without changing its structure.

**Problem** — CSV and pipe-delimited imports share parse-validate-save flow but differ in parsing.

**Applicability** — **Use** when several classes share the same sequence and differ in some steps. **Avoid** a base-class hierarchy when only one or two steps vary: pass them as functions (`run(parse, validate)`) and skip inheritance entirely.

**TypeScript implementation** — `DataImporter.run` is the template; `parse` is `protected abstract`, `validate` and `save` have defaults. `PipeImporter` marks its override with `override` (use `noImplicitOverride`) and calls `super.validate`. Mark the template method as not overridable by convention, since TypeScript has no `final`. Gotcha: subclasses depending on base internals are fragile.

**Consequences** — Reuses the algorithm and enforces order. Inheritance couples subclasses to the base, which is hard to change later.

**Related patterns** — **Strategy** uses composition; **Factory Method** is often one step of a template; **State** covers behaviour that changes over time.
