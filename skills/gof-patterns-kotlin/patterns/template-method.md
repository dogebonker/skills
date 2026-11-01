# Template Method

A base class fixes the order of steps in a final function and lets subclasses fill in the abstract or open ones.

Refs: https://refactoring.guru/design-patterns/template-method/java/example
Example: [examples/template-method.kt](../examples/template-method.kt)

**Intent** — Define the skeleton of an algorithm in a base class and let subclasses override specific steps.

**Problem** — CSV and JSON importers read, parse, validate and store in the same order, but differ in reading and parsing.

**Applicability** — **Use** when several variants share an algorithm's structure and differ in a few steps, and the framework should control the flow. **Avoid** an abstract base class when only one step varies: a higher-order function that takes the step as a lambda is enough.

**Kotlin implementation** — `DataImporter.importFrom` is public and not `open`, so it is final by default in Kotlin and subclasses cannot reorder it. Steps `read` and `parse` are `protected abstract`, while `isValid` and `store` are `protected open` hooks with defaults. `JsonImporter` overrides only the hook it needs. Android's Activity and Fragment lifecycles are this pattern: the framework calls `onCreate`, `onStart` and so on in a fixed order and you override the steps. Gotcha: always call `super` in lifecycle overrides that require it, and do not call open members from a constructor.

**Consequences** — Shared flow in one place and small subclasses. Inheritance couples subclasses to the base class.

**Related patterns** — **Strategy** varies the whole algorithm by composition; **Factory Method** is often one step of a template; **Visitor** for operations over a structure.
